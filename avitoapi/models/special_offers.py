"""Special-offers (SBC gateway) — discount-blast domain.

Avito's SBC ("special-offers") gateway lets sellers blast discounts to
chat history. The five endpoints surface the lifecycle: enumerate
:class:`AvailableOffer` slots → :class:`MultiCreateOffers` to draft →
:class:`MultiConfirmOffers` to commit → stats + tariff probes.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, RootModel

from ._base import BoundModel


class AvailableOffer(BaseModel):
    """One slot returned by ``POST /special-offers/v1/available``."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    item_id: int = Field(..., alias="itemId", description="Avito numeric item id.")
    chat_id: str | None = Field(
        default=None,
        alias="chatId",
        description="Target chat id; ``None`` when the slot is item-only.",
    )
    max_discount_percent: int | None = Field(
        default=None,
        alias="maxDiscountPercent",
        ge=0,
        le=100,
        description="Server-imposed ceiling on the discount.",
    )


class AvailableOfferList(RootModel[list[AvailableOffer]]):
    """Top-level array envelope for available-offer responses."""

    root: list[AvailableOffer] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class OfferConfirmation(BaseModel):
    """One row of ``POST /special-offers/v1/multiConfirm`` result."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    offer_id: str = Field(..., alias="offerId", description="Server-side offer id.")
    confirmed: bool = Field(..., description="True when the offer cleared validation.")
    error: str | None = Field(default=None, description="Human-readable failure reason.")


class OfferConfirmationList(RootModel[list[OfferConfirmation]], BoundModel):
    """Top-level array envelope for multi-confirm responses."""

    root: list[OfferConfirmation] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class OfferCreateResult(BaseModel):
    """One row of ``POST /special-offers/v1/multiCreate`` result."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    offer_id: str = Field(..., alias="offerId", description="Server-side offer id.")
    item_id: int | None = Field(
        default=None,
        alias="itemId",
        description="Linked item id, when surfaced.",
    )
    status: str = Field(
        default="draft",
        description="Lifecycle state (``draft`` / ``pending`` / ``failed``).",
    )


class OfferCreateResultList(RootModel[list[OfferCreateResult]], BoundModel):
    """Top-level array envelope for multi-create responses."""

    root: list[OfferCreateResult] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class OfferStat(BaseModel):
    """One stat row from ``POST /special-offers/v1/stats``."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    offer_id: str = Field(..., alias="offerId", description="Offer id.")
    sent: int = Field(default=0, ge=0, description="Number of times the offer was delivered.")
    accepted: int = Field(default=0, ge=0, description="Number of acceptances.")
    declined: int = Field(default=0, ge=0, description="Number of declines.")
    period_from: datetime | None = Field(
        default=None,
        alias="periodFrom",
        description="Stat window start (UTC).",
    )
    period_to: datetime | None = Field(
        default=None,
        alias="periodTo",
        description="Stat window end (UTC).",
    )


class OfferStatList(RootModel[list[OfferStat]]):
    """Top-level array envelope for stats responses."""

    root: list[OfferStat] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class OfferTariffInfo(BoundModel):
    """Tariff envelope returned by ``POST /special-offers/v1/tariffInfo``."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    daily_limit: int | None = Field(
        default=None,
        alias="dailyLimit",
        description="Per-day cap on offer sends.",
    )
    monthly_limit: int | None = Field(
        default=None,
        alias="monthlyLimit",
        description="Per-month cap on offer sends.",
    )
    used_today: int = Field(
        default=0,
        alias="usedToday",
        ge=0,
        description="Offers sent so far today.",
    )
