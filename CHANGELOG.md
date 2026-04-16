Release Notes
=============

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
