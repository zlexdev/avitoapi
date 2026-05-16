"""Auction domain — CPA auction bids per item.

Avito's CPA auction lets sellers bid per category/region for higher
placement. The two endpoints (``GET`` + ``POST`` on ``/auction/1/bids``)
both deal with the same :class:`AuctionBid` shape.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, RootModel

from ._base import BoundModel


class AuctionBid(BaseModel):
    """One auction bid row — per category / per region."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    category_id: int = Field(..., alias="categoryId", description="Avito category id.")
    region_id: int | None = Field(
        default=None,
        alias="regionId",
        description="Optional region scope; ``None`` means all regions.",
    )
    bid: int = Field(..., ge=0, description="Bid amount in integer rubles.")
    max_bid: int | None = Field(
        default=None,
        alias="maxBid",
        description="Maximum bid cap; only present when auto-bidding is on.",
    )


class AuctionBidList(RootModel[list[AuctionBid]], BoundModel):
    """Top-level array envelope for auction-bids responses.

    Inherits :class:`BoundModel` so the funnel cascades the client into
    contained rows (no bound actions today, but kept for symmetry).
    """

    root: list[AuctionBid] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class SetAuctionBidsResult(BoundModel):
    """Acknowledgement returned by ``POST /auction/1/bids``."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    success: bool = Field(default=True, description="True on 2xx.")
    updated: int | None = Field(
        default=None,
        description="Count of bids accepted; surfaced when Avito reports it.",
    )
