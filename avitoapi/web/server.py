"""Framework-agnostic webhook descriptors + default backend aliases.

This module owns the data types every backend agrees on:

* :class:`Webhook` — one mounted endpoint (path, handler, method).
* :class:`WebhookConfig` — bundle of webhooks + bind address.
* :data:`WebhookHandler` — handler signature.

The bare names ``WebApp`` and ``WebhookRunner`` are aliases to the
aiohttp backend (kept stable for back-compat — aiohttp is the default,
no extra dep). For other frameworks import from
:mod:`avitoapi.web.servers`: ``FastAPIWebhookRunner``,
``LitestarWebhookRunner``, ``SanicWebhookRunner``, etc.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..logging import get_logger

if TYPE_CHECKING:
    from .servers.aiohttp_server import AiohttpWebApp, AiohttpWebhookRunner

log = get_logger(__name__)

WebhookHandler = Callable[[dict[str, Any]], Awaitable[tuple[int, dict[str, Any]]]]


@dataclass(slots=True)
class Webhook:
    """One mounted webhook endpoint.

    ``handler`` receives the JSON body (already parsed into ``dict``) and
    returns ``(status_code, response_body)``. Mount on any backend's
    :class:`~avitoapi.web.servers.BaseWebApp` via
    :meth:`~avitoapi.web.servers.BaseWebApp.register_webhook`.
    """

    path: str
    handler: WebhookHandler
    http_method: str = "POST"


@dataclass(slots=True)
class WebhookConfig:
    """Bundle of :class:`Webhook` descriptors used by any backend runner."""

    host: str = "0.0.0.0"  # nosec B104 — webhooks must be reachable from outside
    port: int = 8080
    webhooks: list[Webhook] = field(default_factory=list)

    def add(self, webhook: Webhook) -> Webhook:
        self.webhooks.append(webhook)
        return webhook


def __getattr__(name: str) -> Any:
    """Lazy-alias ``WebApp`` and ``WebhookRunner`` to the aiohttp backend.

    Kept as module-level lazy aliases (not direct imports) so importing
    :mod:`avitoapi.web.server` does not pull aiohttp eagerly.
    """
    if name == "WebApp":
        from .servers.aiohttp_server import AiohttpWebApp  # noqa: PLC0415 — lazy

        return AiohttpWebApp
    if name == "WebhookRunner":
        from .servers.aiohttp_server import AiohttpWebhookRunner  # noqa: PLC0415 — lazy

        return AiohttpWebhookRunner
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


if TYPE_CHECKING:
    WebApp = AiohttpWebApp
    WebhookRunner = AiohttpWebhookRunner


__all__ = [
    "WebApp",
    "Webhook",
    "WebhookConfig",
    "WebhookHandler",
    "WebhookRunner",
]
