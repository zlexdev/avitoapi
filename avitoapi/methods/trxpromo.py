"""TrxPromo v1 — apply / cancel transaction-commission discounts + list rules."""
from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..models.trxpromo import TrxApplyResult, TrxCancelResult, TrxCommissionList
from ._base import BaseMethod


class ApplyTrxPromo(BaseMethod[TrxApplyResult]):
    """Activate a transaction-commission discount via ``POST /trx-promo/1/apply``.

    Idempotent — the funnel injects an ``Idempotency-Key`` so retried calls
    do not stack two active discounts.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/trx-promo/1/apply"
    __idempotent_mutation__: ClassVar[bool] = True

    promo_code: str = Field(..., min_length=1, description="Promo code to activate.")
    category_ids: list[int] = Field(
        default_factory=list,
        description="Optional category whitelist; empty = applies to all eligible categories.",
    )


class CancelTrxPromo(BaseMethod[TrxCancelResult]):
    """Cancel an active transaction-commission discount via
    ``POST /trx-promo/1/cancel``.

    Idempotent — re-cancelling an already-cancelled promo is a no-op on
    the server.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/trx-promo/1/cancel"
    __idempotent_mutation__: ClassVar[bool] = True

    promo_id: str = Field(..., min_length=1, description="Identifier of the promo to cancel.")


class GetTrxCommissions(BaseMethod[TrxCommissionList]):
    """List the current per-category commission rules via
    ``GET /trx-promo/1/commissions``.
    """

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/trx-promo/1/commissions"
