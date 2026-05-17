"""FastAPI-backed webhook server.

Mounts each :class:`~avitoapi.web.server.Webhook` as a FastAPI route.
The server is driven by ``uvicorn.Server`` programmatically so
``start()``/``stop()`` remain coroutine-friendly (no blocking
``uvicorn.run`` call). ``fastapi`` and ``uvicorn`` are both lazy-imported.
"""
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from ...logging import get_logger
from ._base import BaseWebApp, BaseWebhookRunner

if TYPE_CHECKING:
    from ..server import Webhook

log = get_logger(__name__)


class FastAPIWebApp(BaseWebApp):
    """Thin wrapper around ``fastapi.FastAPI``."""

    def __init__(self) -> None:
        from fastapi import FastAPI  # noqa: PLC0415 — lazy

        self.app: Any = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    def register_webhook(self, webhook: Webhook) -> None:
        from fastapi import Request  # noqa: PLC0415 — lazy
        from fastapi.responses import JSONResponse  # noqa: PLC0415 — lazy

        async def _route(request: Request) -> JSONResponse:
            try:
                body = await request.json()
            except Exception:  # noqa: BLE001 — malformed body classification
                return JSONResponse({"error": "invalid_body"}, status_code=400)
            status, payload = await webhook.handler(body)
            return JSONResponse(payload, status_code=status)

        self.app.add_api_route(
            webhook.path,
            _route,
            methods=[webhook.http_method],
            include_in_schema=False,
        )


class FastAPIWebhookRunner(BaseWebhookRunner):
    """Drive ``uvicorn.Server`` programmatically.

    ``start()`` returns when the server is up and serving (it spawns the
    serve loop as a background task). ``stop()`` sets ``should_exit`` and
    awaits the serve task.
    """

    _server: Any | None
    _serve_task: asyncio.Task[Any] | None

    def _build_app(self) -> BaseWebApp:
        self._server = None
        self._serve_task = None
        return FastAPIWebApp()

    async def start(self) -> None:
        import uvicorn  # noqa: PLC0415 — lazy

        app = self.app
        assert isinstance(app, FastAPIWebApp)
        config = uvicorn.Config(
            app.app,
            host=self.config.host,
            port=self.config.port,
            log_config=None,
            access_log=False,
        )
        self._server = uvicorn.Server(config)
        self._serve_task = asyncio.create_task(self._server.serve())
        # Yield until uvicorn flips its "started" flag (avoids a race
        # where stop() is called before serve() reached its first loop tick).
        while not getattr(self._server, "started", False):
            if self._serve_task.done():
                await self._serve_task
                return
            await asyncio.sleep(0.01)
        log.info(
            "webhook.started",
            backend="fastapi",
            host=self.config.host,
            port=self.config.port,
        )

    async def stop(self) -> None:
        if self._server is not None:
            self._server.should_exit = True
        if self._serve_task is not None:
            try:
                await self._serve_task
            finally:
                self._serve_task = None
                self._server = None
        log.info("webhook.stopped", backend="fastapi")


__all__ = ["FastAPIWebApp", "FastAPIWebhookRunner"]
