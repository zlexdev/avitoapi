"""Litestar-backed webhook server.

Builds a ``litestar.Litestar`` app with one ``Route`` per
:class:`~avitoapi.web.server.Webhook`. Like the FastAPI backend, runs
under ``uvicorn.Server`` programmatically so ``start()``/``stop()``
remain async-safe.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from ...logging import get_logger
from ._base import BaseWebApp, BaseWebhookRunner

if TYPE_CHECKING:
    from ..server import Webhook

log = get_logger(__name__)


class LitestarWebApp(BaseWebApp):
    """Thin wrapper around ``litestar.Litestar``.

    Litestar builds its router from the routes list passed to the
    constructor, so registrations are buffered and committed lazily on
    first access to :attr:`app`.
    """

    def __init__(self) -> None:
        self._routes: list[Any] = []
        self._app: Any | None = None

    @property
    def app(self) -> Any:
        if self._app is None:
            from litestar import Litestar  # noqa: PLC0415 — lazy

            self._app = Litestar(route_handlers=list(self._routes), openapi_config=None)
        return self._app

    @app.setter
    def app(self, value: Any) -> None:
        self._app = value

    def register_webhook(self, webhook: Webhook) -> None:
        if self._app is not None:
            raise RuntimeError(
                "LitestarWebApp.app already materialised — register webhooks before start()",
            )
        from litestar import Request, Response, route  # noqa: PLC0415 — lazy

        # litestar @route decorator strips function type
        @route(path=webhook.path, http_method=[webhook.http_method])  # type: ignore[untyped-decorator]  # litestar decorator strips type
        async def _handler(request: Request[Any, Any, Any]) -> Response[Any]:
            try:
                body = await request.json()
            except Exception:  # noqa: BLE001 — malformed body classification
                return Response({"error": "invalid_body"}, status_code=400)
            status, payload = await webhook.handler(body)
            return Response(payload, status_code=status)

        self._routes.append(_handler)


class LitestarWebhookRunner(BaseWebhookRunner):
    """Drive ``uvicorn.Server`` over the Litestar app."""

    _server: Any | None
    _serve_task: asyncio.Task[Any] | None

    def _build_app(self) -> BaseWebApp:
        self._server = None
        self._serve_task = None
        return LitestarWebApp()

    async def start(self) -> None:
        import uvicorn  # noqa: PLC0415 — lazy

        app: LitestarWebApp = self.app  # type: ignore[assignment]
        config = uvicorn.Config(
            app.app,
            host=self.config.host,
            port=self.config.port,
            log_config=None,
            access_log=False,
        )
        self._server = uvicorn.Server(config)
        self._serve_task = asyncio.create_task(self._server.serve())
        while not getattr(self._server, "started", False):
            if self._serve_task.done():
                await self._serve_task
                return
            await asyncio.sleep(0.01)
        log.info(
            "webhook.started",
            backend="litestar",
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
        log.info("webhook.stopped", backend="litestar")


__all__ = ["LitestarWebApp", "LitestarWebhookRunner"]
