"""Webhook server bits — re-exports ``evented`` web facades + Avito adapter.

The ``evented``-backed names (``WebApp``, ``Webhook``, ``WebhookConfig``,
``WebhookRunner``) are lazy-loaded so importing the package never fails
when the private ``evented`` dep is absent. The Avito-specific Handler
+ middlewares (no evented dependency) are always available.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .avito_webhook_handler import AvitoWebhookHandler, AvitoWebhookParseError

if TYPE_CHECKING:
    from .server import WebApp, Webhook, WebhookConfig, WebhookRunner


def __getattr__(name: str) -> Any:
    if name in {"WebApp", "Webhook", "WebhookConfig", "WebhookRunner"}:
        from . import server

        return getattr(server, name)
    raise AttributeError(f"module 'avitoapi.web' has no attribute {name!r}")


__all__ = [
    "AvitoWebhookHandler",
    "AvitoWebhookParseError",
    "WebApp",
    "Webhook",
    "WebhookConfig",
    "WebhookRunner",
]
