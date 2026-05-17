"""aiohttp-backed webhook server.

Default backend — used by the bare :class:`~avitoapi.web.WebApp` /
:class:`~avitoapi.web.WebhookRunner` aliases. Keeps the original
contract: lazy-imports ``aiohttp``, mounts routes via
``aiohttp.web.Application.router.add_route``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...logging import get_logger
from ._base import BaseWebApp, BaseWebhookRunner

if TYPE_CHECKING:
    from ..server import Webhook

log = get_logger(__name__)


class AiohttpWebApp(BaseWebApp):
    """Thin wrapper around ``aiohttp.web.Application``."""

    def __init__(self) -> None:
        from aiohttp import web  # noqa: PLC0415 — lazy

        self._web = web
        self.app: Any = web.Application()

    def register_webhook(self, webhook: Webhook) -> None:
        async def _route(request: Any) -> Any:
            try:
                body = await request.json()
            except Exception:  # noqa: BLE001 — malformed body classification
                return self._web.json_response({"error": "invalid_body"}, status=400)
            status, payload = await webhook.handler(body)
            return self._web.json_response(payload, status=status)

        self.app.router.add_route(webhook.http_method, webhook.path, _route)


class AiohttpWebhookRunner(BaseWebhookRunner):
    """Boot an ``aiohttp.web.AppRunner`` + ``TCPSite`` pair."""

    _runner: Any | None
    _site: Any | None

    def _build_app(self) -> BaseWebApp:
        self._runner = None
        self._site = None
        return AiohttpWebApp()

    async def start(self) -> None:
        from aiohttp import web  # noqa: PLC0415 — lazy

        app = self.app
        assert isinstance(app, AiohttpWebApp)
        self._runner = web.AppRunner(app.app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, host=self.config.host, port=self.config.port)
        await self._site.start()
        log.info(
            "webhook.started",
            backend="aiohttp",
            host=self.config.host,
            port=self.config.port,
        )

    async def stop(self) -> None:
        if self._site is not None:
            await self._site.stop()
            self._site = None
        if self._runner is not None:
            await self._runner.cleanup()
            self._runner = None
        log.info("webhook.stopped", backend="aiohttp")


__all__ = ["AiohttpWebApp", "AiohttpWebhookRunner"]
