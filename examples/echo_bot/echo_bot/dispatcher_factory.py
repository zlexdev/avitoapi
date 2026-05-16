"""Pre-wires HMAC + idempotency + fast-return middlewares onto a Dispatcher."""
from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from avitoapi.dispatcher import make_dispatcher
from avitoapi.web.middlewares import (
    HMACSignatureMiddleware,
    WebhookFastReturnMiddleware,
    WebhookIdempotencyMiddleware,
)

if TYPE_CHECKING:
    from avitoapi.client import Client
    from avitoapi.storage.base import BaseStorage


def build(
    *,
    accounts: list[Client],
    storage: BaseStorage[Any, str],
    webhook_secret: str,
    require_signature: bool = True,
    idempotency_ttl: timedelta = timedelta(hours=1),
) -> tuple[Any, HMACSignatureMiddleware, WebhookIdempotencyMiddleware, WebhookFastReturnMiddleware]:
    """Build the dispatcher and the three webhook middlewares wired against it.

    Returns ``(dispatcher, hmac_mw, idempotency_mw, fast_return_mw)``.
    """
    dispatcher = make_dispatcher(accounts=accounts)

    async def _secret_provider(_webhook_id: str) -> str | None:
        return webhook_secret

    hmac_mw = HMACSignatureMiddleware(
        _secret_provider,
        require_signature=require_signature,
    )
    idempotency_mw = WebhookIdempotencyMiddleware(storage, ttl=idempotency_ttl)
    fast_return_mw = WebhookFastReturnMiddleware()

    return dispatcher, hmac_mw, idempotency_mw, fast_return_mw
