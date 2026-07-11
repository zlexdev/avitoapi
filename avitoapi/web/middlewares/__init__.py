"""Webhook-side middlewares: signature verification, fast-return.

Deduplication is no longer a webhook concern — it lives once at the dispatch
boundary (``Dispatcher.dedup``), keyed by ``event.dedup_key``, covering every
event kind.
"""

from __future__ import annotations

from .context import WebhookRequestContext
from .fast_return import WebhookFastReturnMiddleware
from .hmac_signature import HMACSignatureMiddleware, SecretProvider

__all__ = [
    "HMACSignatureMiddleware",
    "SecretProvider",
    "WebhookFastReturnMiddleware",
    "WebhookRequestContext",
]
