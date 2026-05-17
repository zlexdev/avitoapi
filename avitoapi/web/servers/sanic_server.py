"""Sanic-backed webhook server.

Uses ``Sanic.create_server`` to keep server lifecycle inside the running
event loop (avoids ``Sanic.run`` which manages its own loop). ``sanic``
is lazy-imported.
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from ...logging import get_logger
from ._base import BaseWebApp, BaseWebhookRunner

if TYPE_CHECKING:
    from ..server import Webhook

log = get_logger(__name__)


class SanicWebApp(BaseWebApp):
    """Thin wrapper around ``sanic.Sanic``."""

    def __init__(self, name: str | None = None) -> None:
        from sanic import Sanic  # noqa: PLC0415 — lazy

        # Sanic enforces unique app names per process; generate a stable
        # default so multiple runners coexist in the same interpreter.
        self.app: Any = Sanic(name or f"avitoapi_{uuid.uuid4().hex[:8]}")

    def register_webhook(self, webhook: Webhook) -> None:
        from sanic.response import json as sanic_json  # noqa: PLC0415 — lazy

        async def _route(request: Any) -> Any:
            try:
                body = request.json
                if body is None:
                    raise ValueError("empty body")
            except Exception:  # noqa: BLE001 — malformed body classification
                return sanic_json({"error": "invalid_body"}, status=400)
            status, payload = await webhook.handler(body)
            return sanic_json(payload, status=status)

        self.app.add_route(
            _route,
            webhook.path,
            methods=[webhook.http_method],
            name=f"webhook_{webhook.http_method}_{webhook.path.strip('/').replace('/', '_') or 'root'}",
        )


class SanicWebhookRunner(BaseWebhookRunner):
    """Boot a Sanic server inside the current event loop."""

    _server: Any | None

    def _build_app(self) -> BaseWebApp:
        self._server = None
        return SanicWebApp()

    async def start(self) -> None:
        app = self.app
        assert isinstance(app, SanicWebApp)
        coro = app.app.create_server(
            host=self.config.host,
            port=self.config.port,
            return_asyncio_server=True,
            access_log=False,
        )
        self._server = await coro
        if self._server is None:
            raise RuntimeError("sanic create_server returned None")
        await self._server.startup()
        await self._server.start_serving()
        log.info(
            "webhook.started",
            backend="sanic",
            host=self.config.host,
            port=self.config.port,
        )

    async def stop(self) -> None:
        if self._server is not None:
            try:
                self._server.close()
                await self._server.wait_closed()
            finally:
                self._server = None
        log.info("webhook.stopped", backend="sanic")


__all__ = ["SanicWebApp", "SanicWebhookRunner"]
