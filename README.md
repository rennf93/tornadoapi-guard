# tornadoapi-guard

---

**tornadoapi-guard is a security library for Tornado that provides middleware to control IPs, log requests, detect penetration attempts and more. It integrates seamlessly with Tornado to offer robust protection against various security threats. Powered by [guard-core](https://github.com/rennf93/guard-core).**

<p align="center">
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
    </a>
    <a href="https://github.com/rennf93/tornadoapi-guard/actions/workflows/ci.yml">
        <img src="https://github.com/rennf93/tornadoapi-guard/actions/workflows/ci.yml/badge.svg" alt="CI">
    </a>
    <a href="https://github.com/rennf93/tornadoapi-guard/actions/workflows/code-ql.yml">
        <img src="https://github.com/rennf93/tornadoapi-guard/actions/workflows/code-ql.yml/badge.svg" alt="CodeQL">
    </a>
    <img src="https://img.shields.io/github/last-commit/rennf93/tornadoapi-guard?style=flat&amp;logo=git&amp;logoColor=white&amp;color=0080ff" alt="last-commit">
</p>

<p align="center">
    <img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&amp;logo=Python&amp;logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Tornado-000000.svg?style=flat&amp;logo=Tornado&amp;logoColor=white" alt="Tornado">
    <img src="https://img.shields.io/badge/Redis-FF4438.svg?style=flat&amp;logo=Redis&amp;logoColor=white" alt="Redis">
</p>

---

Part of the **Guard Security Ecosystem**:

| Framework | Package | Language |
|-----------|---------|----------|
| FastAPI | [fastapi-guard](https://github.com/rennf93/fastapi-guard) | Python |
| Flask | [flaskapi-guard](https://github.com/rennf93/flaskapi-guard) | Python |
| Django | [djapi-guard](https://github.com/rennf93/djapi-guard) | Python |
| Tornado | **tornadoapi-guard** (this) | Python |
| Express/NestJS/Fastify/Hono | [guard-core-ts](https://github.com/rennf93/guard-core-ts) | TypeScript |

___

Features
--------

- **IP Whitelisting and Blacklisting**: Control access based on IP addresses.
- **User Agent Filtering**: Block requests from specific user agents.
- **Rate Limiting**: Limit the number of requests from a single IP.
- **Automatic IP Banning**: Automatically ban IPs after a certain number of suspicious requests.
- **Penetration Attempt Detection**: Detect and log potential penetration attempts.
- **HTTP Security Headers**: Comprehensive security headers management (CSP, HSTS, X-Frame-Options, etc.)
- **Custom Logging**: Log security events to a custom file.
- **Cloud Provider IP Blocking**: Block requests from cloud provider IPs (AWS, GCP, Azure).
- **IP Geolocation**: Use a service like IPInfo.io API to determine the country of an IP address.
- **Distributed State Management**: (Optional) Redis integration for shared security state across instances
- **Flexible Storage**: Redis-enabled distributed storage or in-memory storage for single instance deployments

___

Installation
------------

To install `tornadoapi-guard`, use pip:

```bash
pip install tornadoapi-guard
```

___

Quick Start
-----------

```python
import asyncio
import tornado.web
from tornadoapi_guard import SecurityConfig, SecurityHandler, SecurityMiddleware

config = SecurityConfig(
    rate_limit=100,
    auto_ban_threshold=5,
    enable_penetration_detection=True,
)
middleware = SecurityMiddleware(config=config)


class HelloHandler(SecurityHandler):
    async def get(self) -> None:
        self.write({"message": "hello"})


async def main() -> None:
    await middleware.initialize()
    app = tornado.web.Application(
        [(r"/", HelloHandler)],
        security_middleware=middleware,
    )
    app.listen(8000)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
```

See [`examples/simple_app/main.py`](examples/simple_app/main.py) for a full reference application exercising every decorator and security feature.

___

Documentation
-------------

Full documentation is published at <https://rennf93.github.io/tornadoapi-guard/latest/>, or build locally with `make serve-docs`.

___

Development
-----------

```bash
# Install dependencies
make install-dev

# Run tests locally
make local-test

# Run linters
make lint

# Fix formatting
make fix

# Run all checks
make check-all
```

___

Contributing
------------

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

___

License
-------

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

___

Author
------

Renzo Franceschini - [rennf93@users.noreply.github.com](mailto:rennf93@users.noreply.github.com) .

___

Acknowledgements
----------------

- [Tornado](https://www.tornadoweb.org/)
- [guard-core](https://github.com/rennf93/guard-core)
- [Redis](https://redis.io/)
