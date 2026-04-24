Release Notes
=============

___

v1.0.0 (2026-04-24)
-------------------

Telemetry pipeline wiring fix (v1.0.0)
--------------------------------------

Adopts guard-core 1.1.0 and fixes a middleware wiring bug that prevented OpenTelemetry, Logfire, and event/metric/check-log muting from seeing anything emitted by the request-path security pipeline.

- **Fixed** — `SecurityMiddleware.__init__` previously constructed `SecurityEventBus(agent_handler, ...)` and `MetricsCollector(agent_handler, ...)` directly, using the bare `guard_agent` handler (or `None`). `middleware.initialize()` then called `HandlerInitializer.initialize_agent_integrations()` which built a `CompositeAgentHandler` that no code path ever reached, because the event bus / metrics collector were already frozen on the bare handler. As a result, every event emitted through the request pipeline (`SecurityEventBus.send_middleware_event`) and every request metric bypassed OTel, Logfire, and the configured `muted_event_types` / `muted_metric_types` filter. This release extracts event-bus construction into `_build_event_bus_and_contexts()`, which consults `handler_initializer.composite_handler` and uses `build_event_bus()` / `build_metrics_collector()` when the composite is available. `initialize()` re-invokes `_build_event_bus_and_contexts()` after `initialize_agent_integrations()` so the dependent contexts (`ResponseContext`, `ValidationContext`, `BehavioralContext`) bind to the post-init event bus.
- **Added** — `tests/test_middleware_wiring.py` — four regression tests that pin `mw.event_bus.agent_handler` and `mw.metrics_collector.agent_handler` to `CompositeAgentHandler` after `middleware.initialize()` when OTel or Logfire is enabled, and confirm all dependent contexts reference the post-init event bus.
- **Dependencies** — `guard-core>=1.1.0,<2.0.0`.
- **User-visible impact** — Users already setting `enable_otel=True` or `enable_logfire=True` on `SecurityConfig` were previously getting handler-path events only (ip_banned, rate_limited from `ip_ban_manager` / `rate_limit_handler`, etc.) — but never pipeline-path events (`penetration_attempt`, `authentication_failed`, `user_agent_blocked`, `https_enforced`, etc.) or request metrics (`guard.request.duration`, `guard.request.count`, `guard.error.count`). After this release, every event and every metric flows through the composite, which means OTel spans, Logfire logs, and all mute fields (`muted_event_types`, `muted_metric_types`, `muted_check_logs`) work as documented. No `SecurityConfig` changes required; existing configurations produce strictly more telemetry, not less.

___

v1.0.0 (2026-04-16)
-------------------

Initial Release (v1.0.0)
------------

- **Tornado adapter layer**: `TornadoGuardRequest`, `TornadoGuardResponse`, `TornadoResponseFactory` mapping Tornado's `RequestHandler` to guard-core's protocol interface.
- **SecurityHandler**: Base handler subclass integrating guard-core's security pipeline via `prepare()` / `on_finish()` hooks.
- **SecurityMiddleware**: Full security check pipeline (17 checks) with config via `Application.settings["security_middleware"]`.
- **Public API re-exports**: All guard-core exports available through `tornadoapi_guard` for a clean import surface.
- **Example application**: Comprehensive Tornado app demonstrating IP filtering, rate limiting, behavioral analysis, security headers, decorators, and WebSocket support.
- **Full documentation**: MkDocs site with API reference, configuration guides, decorator usage, and security tutorials.
- **CI/CD**: GitHub Actions workflows for CI, CodeQL, container release, docs deployment, scheduled linting, and PyPI release.
- **Development tooling**: Pre-commit hooks, Makefile targets, Docker Compose setup, Python 3.10-3.14 support.

___

v0.0.1 (2026-04-05)
-------------------

Initial Release (v0.0.1)
------------

- **Initial project scaffolding**: Project structure matching Guard ecosystem conventions.
- **Guard-core integration**: Thin adapter over [guard-core](https://github.com/rennf93/guard-core), the framework-agnostic security engine.
- **Tornado adapters**: `TornadoGuardRequest`, `TornadoGuardResponse`, `TornadoResponseFactory` for mapping Tornado's `RequestHandler` to guard-core interfaces.
- **CI/CD pipeline**: GitHub Actions workflows for CI, release, CodeQL, docs, container release, and scheduled linting.
- **Development tooling**: Pre-commit hooks, Makefile targets, Docker Compose setup, Python 3.10-3.14 support.
