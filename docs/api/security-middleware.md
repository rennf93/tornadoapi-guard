---

title: SecurityMiddleware API - TornadoAPI Guard
description: Complete API reference for TornadoAPI Guard's SecurityMiddleware class and its configuration options
keywords: security middleware, tornado middleware, api security, middleware configuration
---

SecurityMiddleware
==================

`SecurityMiddleware` is the core orchestration object of TornadoAPI Guard. It owns the security pipeline, the event bus, the metrics collector, and the response factory. Unlike FastAPI's `BaseHTTPMiddleware`, Tornado has no built-in `call_next` mechanism, so the middleware exposes its lifecycle as **explicit methods** that the `SecurityHandler` base class calls from `prepare()` (before the handler method runs) and `on_finish()` (after the response is sent). You never register it on the router directly — instead you pass the instance to `tornado.web.Application` as the `security_middleware` setting.

See also the [`SecurityHandler` API](security-handler.md) reference for the base class that invokes the middleware.

___

Class Definition
----------------

```python
class SecurityMiddleware:
    def __init__(self, *, config: SecurityConfig) -> None:
        ...
```

**Arguments:**

- `config` — a `SecurityConfig` instance (keyword-only). Required.

The constructor builds all internal components (rate limit handler, response factory, event bus, metrics collector, route resolver, request validator, behavioral processor, etc.) but does **not** start Redis connections or cloud IP refreshes — that work happens asynchronously in `initialize()`.

___

Architecture Overview
---------------------

Request Processing Flow
-----------------------

In FastAPI, security checks run inside a single `dispatch()` coroutine that wraps `call_next`. Tornado has no such wrapper, so TornadoAPI Guard splits request processing into two halves:

```text
RequestHandler.prepare()
    ↓
SecurityHandler.prepare()
    ↓
1. SecurityMiddleware.apply_pre_flight_headers(handler)
    └─ Writes configured security headers + CORS headers to the handler
    ↓
2. SecurityMiddleware.run_pre_processing(handler)
    ├─ Build TornadoGuardRequest from handler.request
    ├─ Populate request state (route config, client IP, start time)
    ├─ Check passthrough / excluded paths
    ├─ SecurityCheckPipeline.execute()
    │   ├─ RouteConfigCheck
    │   ├─ EmergencyModeCheck
    │   ├─ HttpsEnforcementCheck
    │   ├─ RequestLoggingCheck
    │   ├─ RequestSizeContentCheck
    │   ├─ RequiredHeadersCheck
    │   ├─ AuthenticationCheck
    │   ├─ ReferrerCheck
    │   ├─ CustomValidatorsCheck
    │   ├─ TimeWindowCheck
    │   ├─ CloudIpRefreshCheck
    │   ├─ IpSecurityCheck
    │   ├─ CloudProviderCheck
    │   ├─ UserAgentCheck
    │   ├─ RateLimitCheck
    │   ├─ SuspiciousActivityCheck
    │   └─ CustomRequestCheck
    ├─ If any check returns a blocking response:
    │     └─ Apply security headers, CORS headers, custom modifier → return
    └─ Process behavioral "usage" rules
    ↓
3. Handler method runs (get / post / put / ...)
    ↓
RequestHandler.on_finish()
    ↓
SecurityHandler.on_finish()
    ↓
4. SecurityMiddleware.run_post_processing(handler)
    ├─ Reconstruct response from handler state
    ├─ Collect metrics and emit events
    └─ Process behavioral "return" rules
```

The 17-check security pipeline is identical to the one in fastapi-guard since it lives in `guard_core`. What differs is **where** the pipeline is invoked: the Tornado adapter calls it from `SecurityHandler.prepare()` rather than from a `dispatch` coroutine.

Core Components
---------------

The middleware delegates to these specialized modules (all imported from `guard_core`):

- **SecurityCheckPipeline** — executes security checks in sequence
- **SecurityEventBus** — dispatches security events to the monitoring agent
- **MetricsCollector** — collects request/response metrics
- **HandlerInitializer** — initializes Redis and Agent handlers
- **ErrorResponseFactory** — creates and processes responses
- **RouteConfigResolver** — resolves decorator configurations for a request
- **RequestValidator** — validates request properties
- **BehavioralProcessor** — processes behavioral rules

___

Public Methods
--------------

initialize
----------

```python
async def initialize(self) -> None:
    """
    Build the security pipeline and bring up all async handlers.

    Call this exactly once, after constructing the middleware and before
    starting the Tornado server. Safe to await from `main()`.

    Tasks performed:
        - Build the 17-check security pipeline
        - Initialize Redis handlers (if enable_redis is set)
        - Initialize agent integrations (if enable_agent is set)
    """
```

**Example:**

```python
async def main() -> None:
    await security_middleware.initialize()
    app = build_application()
    app.listen(8000)
    await asyncio.Event().wait()
```

reset
-----

```python
async def reset(self) -> None:
    """
    Release rate-limit state. Call during shutdown.
    """
```

set_decorator_handler
---------------------

```python
def set_decorator_handler(
    self, decorator_handler: BaseSecurityDecorator | None
) -> None:
    """
    Register a SecurityDecorator with the middleware so that route-level
    decorator configurations can be resolved at request time.

    Args:
        decorator_handler: A SecurityDecorator instance or None to clear.
    """
```

Call this once right after creating your `SecurityDecorator` instance.

run_pre_processing
------------------

```python
async def run_pre_processing(
    self, handler: RequestHandler
) -> GuardResponse | None:
    """
    Run the full security pipeline for an incoming request.

    Called automatically by SecurityHandler.prepare(). Returns a
    GuardResponse when any check blocks the request (in which case
    SecurityHandler writes the blocking response back through the
    handler), or None when the request may proceed.

    Args:
        handler: The current Tornado RequestHandler instance.
    """
```

run_post_processing
-------------------

```python
async def run_post_processing(self, handler: RequestHandler) -> None:
    """
    Run post-processing hooks after the handler method has finished.

    Called automatically by SecurityHandler.on_finish(). Performs:
        - Metrics collection
        - Security event emission
        - Behavioral return-pattern processing
    """
```

apply_pre_flight_headers
------------------------

```python
async def apply_pre_flight_headers(self, handler: RequestHandler) -> None:
    """
    Write the configured security headers (CSP, HSTS, frame options, etc.)
    and — if the request carries an Origin header — CORS headers onto the
    handler before the pipeline runs.
    """
```

refresh_cloud_ip_ranges
-----------------------

```python
async def refresh_cloud_ip_ranges(self) -> None:
    """
    Refresh the in-memory (or Redis-cached) cloud provider IP ranges.

    Normally triggered automatically by CloudIpRefreshCheck. Exposed as a
    public method so that application code can force a refresh, e.g. from
    an admin endpoint.
    """
```

create_error_response
---------------------

```python
async def create_error_response(
    self, status_code: int, default_message: str
) -> GuardResponse:
    """
    Create a standardized GuardResponse for a given status code.

    Custom error messages can be configured via
    SecurityConfig.custom_error_responses.
    """
```

___

Registration Pattern
--------------------

Put the middleware, the decorator, and the application together like this:

```python
import asyncio

import tornado.web
from tornadoapi_guard import (
    SecurityConfig,
    SecurityDecorator,
    SecurityMiddleware,
)

config = SecurityConfig(
    enable_rate_limiting=True,
    rate_limit=100,
    rate_limit_window=60,
    enable_redis=True,
    redis_url="redis://localhost:6379",
)

middleware = SecurityMiddleware(config=config)
decorator = SecurityDecorator(config)
middleware.set_decorator_handler(decorator)


async def main() -> None:
    await middleware.initialize()
    app = tornado.web.Application(
        routes,
        security_middleware=middleware,
        guard_decorator=decorator,
    )
    app.listen(8000)
    try:
        await asyncio.Event().wait()
    finally:
        await middleware.reset()


if __name__ == "__main__":
    asyncio.run(main())
```

**Important:** both `security_middleware` and `guard_decorator` must be passed as `tornado.web.Application` settings. `SecurityHandler.prepare()` looks up `security_middleware` from `self.application.settings`, and the middleware looks up `guard_decorator` from the same place when resolving route configurations.

___

Handler Integration
-------------------

The middleware works with singleton handler instances imported from `guard_core`:

- All handler classes (`IPBanManager`, `CloudManager`, etc.) use the singleton pattern.
- The middleware initializes these existing instances conditionally based on configuration.
- `IPInfoManager` is only initialized when country filtering is enabled.
- `CloudManager` is only loaded when cloud provider blocking is configured.
- This selective loading improves startup time when not all features are used.

___

Redis Configuration
-------------------

Enable Redis in `SecurityConfig`:

```python
config = SecurityConfig(
    enable_redis=True,
    redis_url="redis://prod:6379/0",
    redis_prefix="prod_security:",
)
```

The middleware's `initialize()` method will bring up:

- `CloudManager` cloud provider IP ranges
- `IPBanManager` distributed banning
- `IPInfoManager` IP geolocation
- `RateLimitManager` rate limiting
- `RedisManager` Redis caching
- `SusPatternsManager` suspicious patterns

___

Proxy Security Configuration
----------------------------

The middleware supports secure handling of proxy headers:

```python
config = SecurityConfig(
    trusted_proxies=["10.0.0.1", "192.168.1.0/24"],
    trusted_proxy_depth=1,
    trust_x_forwarded_proto=True,
)
```

This prevents IP spoofing attacks through header manipulation.

___

See Also
--------

- [SecurityHandler](security-handler.md) - Base class that invokes the middleware from `prepare` and `on_finish`
- [Decorators](decorators.md) - Route-level security decorators
- [API Overview](overview.md) - Complete API reference
