from __future__ import annotations

import asyncio

from guard_core.sync.handlers.cors_handler import CorsHandler, is_preflight
from tornado.web import RequestHandler

from tornadoapi_guard.adapters import apply_guard_response
from tornadoapi_guard.middleware import SecurityMiddleware

_background_tasks: set[asyncio.Task[None]] = set()


class SecurityHandler(RequestHandler):
    async def prepare(self) -> None:
        middleware = self._get_security_middleware()
        if middleware is None:
            return

        await middleware.apply_pre_flight_headers(self)

        blocking = await middleware.run_pre_processing(self)
        cors_handler = _build_cors_handler(middleware)

        if blocking is not None:
            _apply_cors_response_headers(self, cors_handler)
            apply_guard_response(self, blocking)
            return

        if _handle_preflight(self, cors_handler):
            return

        _apply_cors_response_headers(self, cors_handler)

    def on_finish(self) -> None:
        middleware = self._get_security_middleware()
        if middleware is None:
            return
        task = asyncio.create_task(middleware.run_post_processing(self))
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)

    def _get_security_middleware(self) -> SecurityMiddleware | None:
        value = self.application.settings.get("security_middleware")
        if isinstance(value, SecurityMiddleware):
            return value
        return None


def _build_cors_handler(middleware: SecurityMiddleware) -> CorsHandler | None:
    if not middleware.config.enable_cors:
        return None
    return CorsHandler(middleware.config)


def _apply_cors_response_headers(
    handler: RequestHandler, cors_handler: CorsHandler | None
) -> None:
    if cors_handler is None:
        return
    for k, v in cors_handler.build_response_headers(
        dict(handler.request.headers)
    ).items():
        handler.set_header(k, v)


def _handle_preflight(
    handler: RequestHandler, cors_handler: CorsHandler | None
) -> bool:
    if cors_handler is None:
        return False
    if not is_preflight(handler.request.method or "", dict(handler.request.headers)):
        return False
    preflight = cors_handler.build_preflight_response(dict(handler.request.headers))
    handler.set_status(preflight.status_code)
    for k, v in preflight.headers.items():
        handler.set_header(k, v)
    handler.write(preflight.body)
    handler.finish()
    return True
