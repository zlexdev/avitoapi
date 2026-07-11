"""Typed context carrier for the webhook-side middleware chain."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class WebhookRequestContext:
    """Per-request data passed through :class:`~avitoapi.routers.MiddlewareChain`
    for webhook deliveries.

    ``raw_body`` and ``headers`` are available from the start (HMAC verify
    reads them). ``chat_id`` / ``message_id`` are populated by
    :class:`~avitoapi.web.AvitoWebhookHandler` after parsing, for tracing and
    for any custom middleware. Deduplication happens at the dispatch boundary
    (``Dispatcher.dedup``), not here.
    """

    raw_body: bytes
    headers: dict[str, str] = field(default_factory=dict)
    webhook_id: str = ""
    # Enriched by the handler after parsing:
    chat_id: str = ""
    message_id: str = ""


__all__ = ["WebhookRequestContext"]
