"""Special-offers (SBC gateway) endpoints — discount-blast lifecycle.

Five POST endpoints. The mutating ones (``MultiConfirmOffers``,
``MultiCreateOffers``) declare ``__idempotent_mutation__ = True`` so
retries reuse the same idempotency key.
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from ..models.special_offers import (
    AvailableOfferList,
    OfferConfirmationList,
    OfferCreateResultList,
    OfferStatList,
    OfferTariffInfo,
)
from ._base import BaseMethod


class OfferDraft(BaseModel):
    """One row in the body of ``POST /special-offers/v1/multiCreate``."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    item_id: int = Field(..., alias="itemId", ge=1)
    chat_id: str | None = Field(default=None, alias="chatId")
    discount_percent: int = Field(..., ge=1, le=100, alias="discountPercent")


class GetAvailableOffers(BaseMethod[AvailableOfferList]):
    """Enumerate eligible offer slots via ``POST /special-offers/v1/available``.

    Args:
        item_ids: Item ids to probe; Avito returns one slot per matching pair.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/special-offers/v1/available"

    item_ids: list[int] = Field(..., min_length=1)


class MultiConfirmOffers(BaseMethod[OfferConfirmationList]):
    """Commit drafted offers via ``POST /special-offers/v1/multiConfirm``.

    Idempotent — same payload + same idempotency key = same commits.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/special-offers/v1/multiConfirm"
    __idempotent_mutation__: ClassVar[bool] = True

    offer_ids: list[str] = Field(..., min_length=1, description="Drafts to confirm.")


class MultiCreateOffers(BaseMethod[OfferCreateResultList]):
    """Draft new offers via ``POST /special-offers/v1/multiCreate``.

    Idempotent — same payload + same idempotency key = same drafts.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/special-offers/v1/multiCreate"
    __idempotent_mutation__: ClassVar[bool] = True

    offers: list[OfferDraft] = Field(..., min_length=1, description="Offer drafts.")


class GetOffersStats(BaseMethod[OfferStatList]):
    """Per-offer stats via ``POST /special-offers/v1/stats``.

    Args:
        offer_ids: Offers to report on.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/special-offers/v1/stats"

    offer_ids: list[str] = Field(..., min_length=1)


class GetOfferTariffInfo(BaseMethod[OfferTariffInfo]):
    """Tariff probe via ``POST /special-offers/v1/tariffInfo``.

    POST despite being a read — Avito's wire requires an empty JSON
    body on this endpoint, not a GET.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/special-offers/v1/tariffInfo"
