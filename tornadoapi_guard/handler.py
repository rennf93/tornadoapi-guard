from __future__ import annotations

import asyncio

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
        if blocking is not None:
            apply_guard_response(self, blocking)
            return

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
