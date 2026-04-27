from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
import tornado.httpserver
import tornado.netutil
import tornado.web
from guard_core.models import SecurityConfig
from tornado.httpclient import AsyncHTTPClient, HTTPClientError

from tornadoapi_guard import SecurityHandler, SecurityMiddleware


class HelloHandler(SecurityHandler):
    async def get(self) -> None:
        self.write({"ok": True})


async def _start_server(
    config: SecurityConfig,
) -> tuple[tornado.httpserver.HTTPServer, int, SecurityMiddleware]:
    middleware = SecurityMiddleware(config=config)
    await middleware.initialize()
    app = tornado.web.Application(
        [(r"/", HelloHandler)],
        security_middleware=middleware,
    )
    sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    port = sockets[0].getsockname()[1]
    return server, port, middleware


@pytest.fixture
async def hello_app() -> AsyncGenerator[tuple[int, SecurityMiddleware], None]:
    config = SecurityConfig(
        geo_ip_handler=None,
        enable_redis=False,
        enable_penetration_detection=False,
        whitelist=[],
        blacklist=[],
        security_headers={
            "enabled": True,
            "frame_options": "DENY",
            "content_type_options": "nosniff",
        },
    )
    server, port, middleware = await _start_server(config)
    try:
        yield port, middleware
    finally:
        server.stop()
        await middleware.reset()


@pytest.fixture
async def blacklist_app() -> AsyncGenerator[tuple[int, SecurityMiddleware], None]:
    config = SecurityConfig(
        geo_ip_handler=None,
        enable_redis=False,
        enable_penetration_detection=False,
        blacklist=["127.0.0.1"],
        custom_error_responses={403: "Custom Forbidden"},
    )
    server, port, middleware = await _start_server(config)
    try:
        yield port, middleware
    finally:
        server.stop()
        await middleware.reset()


async def test_basic_request_succeeds(
    hello_app: tuple[int, SecurityMiddleware],
) -> None:
    port, _ = hello_app
    client = AsyncHTTPClient()
    try:
        response = await client.fetch(f"http://127.0.0.1:{port}/")
        assert response.code == 200
        assert b'"ok"' in response.body
    finally:
        client.close()


async def test_security_headers_applied(
    hello_app: tuple[int, SecurityMiddleware],
) -> None:
    port, _ = hello_app
    client = AsyncHTTPClient()
    try:
        response = await client.fetch(f"http://127.0.0.1:{port}/")
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
    finally:
        client.close()


async def test_blacklisted_ip_blocked(
    blacklist_app: tuple[int, SecurityMiddleware],
) -> None:
    port, _ = blacklist_app
    client = AsyncHTTPClient()
    try:
        with pytest.raises(HTTPClientError) as exc_info:
            await client.fetch(f"http://127.0.0.1:{port}/")
        assert exc_info.value.code == 403
    finally:
        client.close()
