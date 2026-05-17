"""CpxPromo v1 — per-item target-action pricing.

The CpxPromo product mixes a single GET (``getBids/{itemId}``) with four
POST endpoints. The three state-mutating actions (``remove`` / ``setAuto``
/ ``setManual``) are flagged ``__idempotent_mutation__`` so retries do not
double-apply.
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..models.cpxpromo import CpxActionResult, CpxBidList, CpxPromotionList
from ._base import BaseMethod


class GetCpxBids(BaseMethod[CpxBidList]):
    """Fetch the current bids for one item via
    ``GET /cpxpromo/1/getBids/{item_id}``.

    The placeholder name in the endpoint matches the Pydantic field name
    (``item_id``); the rendered URL is identical to Avito's documented
    ``getBids/{itemId}`` since the placeholder is just a template token.
    """

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/cpxpromo/1/getBids/{item_id}"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"item_id"})

    item_id: int = Field(..., ge=1, description="Item whose bids should be fetched.")


class GetCpxPromotionsByItems(BaseMethod[CpxPromotionList]):
    """Fetch the current promotion mode for a batch of items via
    ``POST /cpxpromo/1/getPromotionsByItemIds``.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/cpxpromo/1/getPromotionsByItemIds"

    item_ids: list[int] = Field(
        ...,
        min_length=1,
        description="Items to query (at least one).",
    )


class RemoveCpxPromotion(BaseMethod[CpxActionResult]):
    """Remove the CpxPromo configuration on the given items via
    ``POST /cpxpromo/1/remove``.

    Idempotent — the funnel injects an ``Idempotency-Key`` so retries are
    safe.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/cpxpromo/1/remove"
    __idempotent_mutation__: ClassVar[bool] = True

    item_ids: list[int] = Field(..., min_length=1)


class SetCpxAutoPromotion(BaseMethod[CpxActionResult]):
    """Switch the given items to auto-bidding via
    ``POST /cpxpromo/1/setAuto``.

    Idempotent — re-applying the same auto mode is a no-op on the server.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/cpxpromo/1/setAuto"
    __idempotent_mutation__: ClassVar[bool] = True

    item_ids: list[int] = Field(..., min_length=1)


class SetCpxManualPromotion(BaseMethod[CpxActionResult]):
    """Set a manual bid for the given items via
    ``POST /cpxpromo/1/setManual``.

    Idempotent — re-applying the same bid is a no-op on the server.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/cpxpromo/1/setManual"
    __idempotent_mutation__: ClassVar[bool] = True

    item_ids: list[int] = Field(..., min_length=1)
    bid: int = Field(..., ge=0, description="Manual bid in rubles.")
