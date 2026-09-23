---

title: SecurityHandler API - TornadoAPI Guard
description: Complete API reference for TornadoAPI Guard's SecurityHandler base class and its lifecycle hooks
keywords: tornado, security, middleware, request handler, lifecycle hooks, prepare, on_finish
---

SecurityHandler
===============

The `SecurityHandler` class is the Tornado-specific base class that every handler inherits from in order to participate in the `tornadoapi-guard` security pipeline.

!!! info "Why a base handler instead of middleware?"
    Tornado does not have an application-level middleware chain like ASGI frameworks (FastAPI, Starlette). There is no `app.add_middleware(...)` equivalent. Instead, Tornado exposes pre-/post-processing hooks on `tornado.web.RequestHandler` (`prepare`, `on_finish`). `tornadoapi-guard` plugs into these hooks through a base class: subclassing `SecurityHandler` is what "attaches" the security pipeline to a route.

___

Class Signature
---------------

```python
from tornado.web import RequestHandler


class SecurityHandler(RequestHandler):
    async def prepare(self) -> None: ...
    def on_finish(self) -> None: ...
    def _get_security_middleware(self) -> SecurityMiddleware | None: ...
```

Subclass `SecurityHandler` for every handler that needs security checks. Handlers that should run outside the pipeline (for example, a public `/health` endpoint) can keep inheriting from `tornado.web.RequestHandler` directly, or can be added to `SecurityConfig.exclude_paths`.

___

Lifecycle Hook: `prepare`
-------------------------

```python
async def prepare(self) -> None:
    middleware = self._get_security_middleware()
    if middleware is None:
        return

    await middleware.apply_pre_flight_headers(self)

    blocking = await middleware.run_pre_processing(self)
    if blocking is not None:
        apply_guard_response(self, blocking)
        return
```

`prepare()` runs **before** the HTTP method (`get`, `post`, etc.) is dispatched. `SecurityHandler` overrides it to:

1. Look up the middleware via `self.application.settings["security_middleware"]`.
2. Call `middleware.apply_pre_flight_headers(self)` to set security and CORS headers on the response (so headers are present even if the handler later writes an error or short-circuits).
3. Call `middleware.run_pre_processing(self)` to execute the 17-check security pipeline (route config, emergency mode, HTTPS enforcement, request logging, request size/content, required headers, authentication, referrer, custom validators, time window, cloud IP refresh, IP security, cloud provider, user agent, rate limit, suspicious activity, and custom request check).
4. If the pipeline returns a blocking response, `apply_guard_response()` writes the status, headers, and body back through the handler (via `clear`, `set_status`, `set_header`, `write`, `finish`). The actual HTTP method is **not** invoked.

Because `prepare()` is `async`, the pipeline can perform async work (Redis lookups, IPInfo API calls, agent event publishing) without blocking the Tornado IOLoop.

___

Lifecycle Hook: `on_finish`
---------------------------

```python
def on_finish(self) -> None:
    middleware = self._get_security_middleware()
    if middleware is None:
        return
    asyncio.create_task(middleware.run_post_processing(self))
```

`on_finish()` runs **after** the response has been sent to the client. `SecurityHandler` overrides it to schedule `middleware.run_post_processing(self)` via `asyncio.create_task`. Post-processing includes:

- Behavioral return-rule processing (for example, "ban after N `404` responses in 60 s").
- Metrics emission (response time, status code, route).
- Event publishing to the Guard Agent (if configured).

Running post-processing as a fire-and-forget task keeps the response path fast: the client sees the response as soon as the handler finishes, and book-keeping happens in the background.

___

Internal Lookup: `_get_security_middleware`
-------------------------------------------

```python
def _get_security_middleware(self) -> SecurityMiddleware | None:
    value = self.application.settings.get("security_middleware")
    if isinstance(value, SecurityMiddleware):
        return value
    return None
```

Internal lookup. Returns the `SecurityMiddleware` instance stored in `application.settings["security_middleware"]`, or `None` if no middleware is configured. When `None` is returned, both `prepare()` and `on_finish()` short-circuit — see [Degraded mode](#degraded-mode) below.

___

Registration
------------

The `SecurityMiddleware` instance is attached to the Tornado `Application` via a settings entry named `security_middleware`. `SecurityHandler` looks it up from there on every request.

```python
import asyncio

import tornado.web

from tornadoapi_guard import SecurityConfig, SecurityHandler, SecurityMiddleware

config = SecurityConfig(
    rate_limit=100,
    enable_rate_limiting=True,
    enable_redis=False,
)
middleware = SecurityMiddleware(config=config)


class MyHandler(SecurityHandler):
    async def get(self) -> None:
        self.write({"status": "ok"})


async def main() -> None:
    await middleware.initialize()
    app = tornado.web.Application(
        [(r"/", MyHandler)],
        security_middleware=middleware,
    )
    app.listen(8000)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
```

Two things to notice:

- `await middleware.initialize()` must run **before** the application starts serving requests. It builds the security pipeline, initializes Redis handlers, and wires up agent integrations.
- The keyword argument `security_middleware=middleware` placed on `tornado.web.Application(...)` ends up in `app.settings["security_middleware"]`, which is exactly where `SecurityHandler._get_security_middleware` reads it from.

___

Combining with `tornado.websocket.WebSocketHandler`
---------------------------------------------------

`SecurityHandler` extends `tornado.web.RequestHandler`, not `tornado.websocket.WebSocketHandler`. WebSocket handlers therefore do **not** flow through the `tornadoapi-guard` pipeline — `prepare()` is not overridden for them and the middleware's security checks will not run.

If you need to protect a WebSocket endpoint, implement the checks directly on the WebSocket handler:

```python
import tornado.websocket


class ProtectedWebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin: str) -> bool:
        return origin in {"https://example.com", "https://app.example.com"}

    async def open(self) -> None:
        token = self.request.headers.get("Authorization")
        if not token or not await verify_token(token):
            self.close(code=4401, reason="unauthorized")
            return
```

The example application in `examples/simple_app/main.py` ships with an `EchoWebSocketHandler` that demonstrates this pattern.

___

Interaction with `set_default_headers`
--------------------------------------

`tornadoapi-guard` does **not** override `set_default_headers` on `SecurityHandler`. Security headers are applied in `prepare()` via `apply_pre_flight_headers` instead, for one reason: the `SecurityHeadersManager.get_headers()` method is asynchronous (it may read configuration from Redis), and Tornado's `set_default_headers` is **synchronous**. An async operation cannot complete inside a sync hook.

This has two practical consequences:

1. You are free to override `set_default_headers` on your own handlers to add static headers (for example, `X-Service-Name`). The headers you set there are applied first, and `apply_pre_flight_headers` then adds (or overrides) the guard-managed security and CORS headers on top.
2. The guard-managed headers are attached even when the pipeline returns a blocking response, because `apply_pre_flight_headers` runs **before** `run_pre_processing`. A client that is rate-limited will still receive the correct `Content-Security-Policy`, `X-Frame-Options`, and CORS headers on the `429` response.

___

Degraded Mode
-------------

If a handler inherits from `SecurityHandler` but the `Application` does **not** have a `security_middleware` entry in its settings (for example, in a unit test, a minimal sandbox, or during local development without the full middleware stack), `_get_security_middleware()` returns `None` and both hooks short-circuit:

- `prepare()` returns immediately — no headers are injected, no pipeline runs.
- `on_finish()` returns immediately — no post-processing is scheduled.

In this degraded state `SecurityHandler` behaves exactly like a plain `tornado.web.RequestHandler`. This is intentional: it lets you write test fixtures that instantiate handlers without having to stand up a full `SecurityMiddleware` and its Redis/agent dependencies. Just remember that **no security checks are being performed** when the middleware is absent.

___

See Also
--------

- [SecurityMiddleware](security-middleware.md) — the orchestration layer that `SecurityHandler` delegates to.
- [Adapters](adapters.md) — `TornadoGuardRequest` / `TornadoGuardResponse` and `apply_guard_response()`.
- [SecurityDecorators](decorators.md) — route-level security via decorators on handler methods.
- [API Overview](overview.md) — complete API reference.
