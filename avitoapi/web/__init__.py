"""Webhook server bits — multi-backend WebApp/Runner + Avito adapter.

The bare ``WebApp`` / ``WebhookRunner`` names alias the aiohttp backend
(zero extra deps). For FastAPI / Litestar / Sanic, import the explicit
class from :mod:`avitoapi.web.servers`. Every backend is lazy-loaded so
importing :mod:`avitoapi.web` never pulls a transitive HTTP framework.

The Avito-specific handler + middlewares (no extra deps) are always
available eagerly.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .avito_webhook_handler import AvitoWebhookHandler, AvitoWebhookParseError
from .server import Webhook, WebhookConfig, WebhookHandler

if TYPE_CHECKING:
    from .server import WebApp, WebhookRunner
    from .servers._base import BaseWebApp, BaseWebhookRunner
    from .servers.aiohttp_server import AiohttpWebApp, AiohttpWebhookRunner
    from .servers.fastapi_server import FastAPIWebApp, FastAPIWebhookRunner
    from .servers.litestar_server import LitestarWebApp, LitestarWebhookRunner
    from .servers.sanic_server import SanicWebApp, SanicWebhookRunner


_LAZY_SERVER = {"WebApp", "WebhookRunner"}
_LAZY_BACKENDS = {
    "AiohttpWebApp",
    "AiohttpWebhookRunner",
    "BaseWebApp",
    "BaseWebhookRunner",
    "FastAPIWebApp",
    "FastAPIWebhookRunner",
    "LitestarWebApp",
    "LitestarWebhookRunner",
    "SanicWebApp",
    "SanicWebhookRunner",
}


def __getattr__(name: str) -> Any:
    if name in _LAZY_SERVER:
        from . import server  # noqa: PLC0415 — lazy

        return getattr(server, name)
    if name in _LAZY_BACKENDS:
        from . import servers  # noqa: PLC0415 — lazy

        return getattr(servers, name)
    raise AttributeError(f"module 'avitoapi.web' has no attribute {name!r}")


__all__ = [
    "AiohttpWebApp",
    "AiohttpWebhookRunner",
    "AvitoWebhookHandler",
    "AvitoWebhookParseError",
    "BaseWebApp",
    "BaseWebhookRunner",
    "FastAPIWebApp",
    "FastAPIWebhookRunner",
    "LitestarWebApp",
    "LitestarWebhookRunner",
    "SanicWebApp",
    "SanicWebhookRunner",
    "WebApp",
    "Webhook",
    "WebhookConfig",
    "WebhookHandler",
    "WebhookRunner",
]
