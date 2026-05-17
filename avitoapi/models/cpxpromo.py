"""CpxPromo domain — per-item target-action pricing config.

Avito's CpxPromo product lets sellers pay per target action (call / chat /
contact) on a per-item basis. The domain exposes the current bids
(``GetBids``), the per-item promotion state (``GetPromotionsByItems``), and
the three state-mutating actions (``remove`` / ``setAuto`` / ``setManual``).

All response DTOs use ``ConfigDict(strict=False, extra="allow")`` — the
Avito payload schema for this surface is sparsely documented and likely to
drift.
"""

from __future__ import annotations

from collections.abc import Iterator
from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, RootModel

from ._base import BoundModel

if TYPE_CHECKING:
    from ..methods.cpxpromo import (
        RemoveCpxPromotion,
        SetCpxAutoPromotion,
        SetCpxManualPromotion,
    )


class CpxPromotionStatus(StrEnum):
    """Per-item CpxPromo mode."""

    AUTO = "auto"
    MANUAL = "manual"
    OFF = "off"


class CpxBid(BaseModel):
    """One bid row returned by ``GetCpxBids``.

    Bids are integer rubles on the Avito wire (no fractional kopecks on
    target-action pricing).
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    item_id: int = Field(..., ge=1, description="Item the bid belongs to.")
    current_bid: int = Field(..., ge=0, description="Seller's current bid in rubles.")
    min_bid: int | None = Field(default=None, ge=0, description="Minimum acceptable bid.")
    recommended: int | None = Field(
        default=None,
        ge=0,
        description="Server-recommended bid, when surfaced.",
    )


class CpxBidList(RootModel[list[CpxBid]]):
    """Top-level JSON array envelope for the CpxPromo bids response."""

    root: list[CpxBid] = Field(default_factory=list)

    def __iter__(self) -> Iterator[CpxBid]:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class CpxPromotion(BoundModel):
    """One per-item CpxPromo state row.

    Bound methods build awaitable method-classes pre-attached to the client;
    manually constructed promotions (no client) raise
    :class:`~avitoapi.exceptions.ModelNotBoundError` on those actions.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    item_id: int = Field(..., ge=1, description="Item under (or eligible for) promotion.")
    mode: CpxPromotionStatus = Field(..., description="Current promotion mode for this item.")
    bid: int | None = Field(
        default=None,
        ge=0,
        description="Manual bid in rubles; absent when mode is auto or off.",
    )

    def remove(self) -> RemoveCpxPromotion:
        """Build an awaitable remove-promotion method-class for this item."""
        from ..methods.cpxpromo import RemoveCpxPromotion

        client = self._require_client()
        return RemoveCpxPromotion(item_ids=[self.item_id]).as_(client)

    def set_auto(self) -> SetCpxAutoPromotion:
        """Build an awaitable set-auto method-class for this item."""
        from ..methods.cpxpromo import SetCpxAutoPromotion

        client = self._require_client()
        return SetCpxAutoPromotion(item_ids=[self.item_id]).as_(client)

    def set_manual(self, bid: int) -> SetCpxManualPromotion:
        """Build an awaitable set-manual method-class with the given bid (rubles)."""
        from ..methods.cpxpromo import SetCpxManualPromotion

        client = self._require_client()
        return SetCpxManualPromotion(item_ids=[self.item_id], bid=bid).as_(client)


class CpxPromotionList(RootModel[list[CpxPromotion]]):
    """Top-level JSON array envelope for ``GetCpxPromotionsByItems``."""

    root: list[CpxPromotion] = Field(default_factory=list)

    def __iter__(self) -> Iterator[CpxPromotion]:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class CpxActionResult(BaseModel):
    """Acknowledgement DTO for the three CpxPromo state-mutating actions.

    Avito's bulk endpoints surface a per-item ok/err map plus an aggregate
    success flag; ``extra="allow"`` preserves unknown keys.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    ok: bool | None = Field(default=None, description="Aggregate success flag, when surfaced.")
    affected: list[int] = Field(
        default_factory=list,
        description="Item ids the action successfully applied to.",
    )
    failed: list[int] = Field(
        default_factory=list,
        description="Item ids that failed (caller should inspect raw payload for cause).",
    )
