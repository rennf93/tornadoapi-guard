Release Notes
=============

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
