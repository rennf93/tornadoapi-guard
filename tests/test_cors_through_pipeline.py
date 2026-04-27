from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
import tornado.httpserver
import tornado.netutil
import tornado.web
from guard_core.models import SecurityConfig
from tornado.httpclient import AsyncHTTPClient

from tornadoapi_guard import SecurityHandler, SecurityMiddleware


class _RootHandler(SecurityHandler):
    def get(self) -> None:
        self.write({"ok": "yes"})

    def post(self) -> None:
        self.write({"ok": "yes"})


def _make_app(
    config: SecurityConfig,
) -> tuple[tornado.web.Application, SecurityMiddleware]:
    middleware = SecurityMiddleware(config=config)
    app = tornado.web.Application(
        [(r"/", _RootHandler)],
        security_middleware=middleware,
    )
    return app, middleware


@pytest.fixture
async def cors_server() -> AsyncGenerator[tuple[int, SecurityMiddleware], None]:
    config = SecurityConfig(
        enable_cors=True,
        cors_allow_origins=["https://app.example.com"],
        cors_allow_methods=["GET", "POST"],
        cors_allow_headers=["X-Custom"],
        cors_allow_credentials=True,
        cors_max_age=600,
        blacklist=["10.0.0.99"],
        trusted_proxies=["127.0.0.1"],
        enable_redis=False,
    )
    app, middleware = _make_app(config)
    await middleware.initialize()
    sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    port: int = sockets[0].getsockname()[1]
    try:
        yield port, middleware
    finally:
        server.stop()
        await middleware.reset()


async def test_preflight_allowed_for_legitimate_origin(
    cors_server: tuple[int, SecurityMiddleware],
) -> None:
    port, _ = cors_server
    client = AsyncHTTPClient()
    try:
        response = await client.fetch(
            f"http://127.0.0.1:{port}/",
            method="OPTIONS",
            allow_nonstandard_methods=True,
            headers={
                "Origin": "https://app.example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.code == 200
        assert (
            response.headers.get("Access-Control-Allow-Origin")
            == "https://app.example.com"
        )
    finally:
        client.close()


async def test_preflight_blocked_for_banned_ip(
    cors_server: tuple[int, SecurityMiddleware],
) -> None:
    port, _ = cors_server
    client = AsyncHTTPClient()
    try:
        response = await client.fetch(
            f"http://127.0.0.1:{port}/",
            method="OPTIONS",
            allow_nonstandard_methods=True,
            headers={
                "Origin": "https://app.example.com",
                "Access-Control-Request-Method": "POST",
                "X-Forwarded-For": "10.0.0.99",
            },
            raise_error=False,
        )
        assert response.code == 403
    finally:
        client.close()


async def test_normal_request_carries_cors_headers(
    cors_server: tuple[int, SecurityMiddleware],
) -> None:
    port, _ = cors_server
    client = AsyncHTTPClient()
    try:
        response = await client.fetch(
            f"http://127.0.0.1:{port}/",
            method="GET",
            headers={"Origin": "https://app.example.com"},
        )
        assert response.code == 200
        assert (
            response.headers.get("Access-Control-Allow-Origin")
            == "https://app.example.com"
        )
        assert response.headers.get("Access-Control-Allow-Credentials") == "true"
    finally:
        client.close()
