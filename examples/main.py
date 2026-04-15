from __future__ import annotations

import asyncio
import os

import tornado.web

from tornadoapi_guard import (
    SecurityConfig,
    SecurityDecorator,
    SecurityHandler,
    SecurityMiddleware,
)


def build_config() -> SecurityConfig:
    return SecurityConfig(
        rate_limit=100,
        rate_limit_window=60,
        enable_redis=bool(os.getenv("REDIS_URL")),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
        redis_prefix=os.getenv("REDIS_PREFIX", "tornadoapi_guard_example"),
        enable_ip_banning=True,
        auto_ban_threshold=5,
        auto_ban_duration=3600,
        enable_penetration_detection=True,
        security_headers={
            "enabled": True,
            "hsts": {"max_age": 31536000, "include_subdomains": True},
            "frame_options": "DENY",
            "content_type_options": "nosniff",
        },
        enable_cors=True,
        cors_allow_origins=["*"],
        cors_allow_methods=["GET", "POST"],
        cors_allow_headers=["*"],
    )


class HelloHandler(SecurityHandler):
    async def get(self) -> None:
        self.write({"message": "hello from tornadoapi-guard"})


class EchoHandler(SecurityHandler):
    async def post(self) -> None:
        self.set_header("Content-Type", "application/json")
        self.write({"received": self.request.body.decode("utf-8", errors="replace")})


async def main() -> None:
    config = build_config()
    middleware = SecurityMiddleware(config=config)
    decorator = SecurityDecorator(config)
    middleware.set_decorator_handler(decorator)
    await middleware.initialize()

    app = tornado.web.Application(
        [
            (r"/", HelloHandler),
            (r"/echo", EchoHandler),
        ],
        security_middleware=middleware,
        guard_decorator=decorator,
    )
    port = int(os.getenv("PORT", "8000"))
    app.listen(port)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
