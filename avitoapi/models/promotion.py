"""Promotion domain — active promotions, bids, BBIP orders + forecast."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, RootModel

from .common import Money


class Promotion(BaseModel):
    """One active promotion row from ``GET /promotion/v1/items``."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    item_id: int = Field(..., ge=1, description="Item under promotion.")
    service: str = Field(..., description="Promotion service slug.")
    expires_at: datetime = Field(..., description="When the active promotion expires (UTC).")


class Bid(BaseModel):
    """One bid row from ``GET /promotion/v1/items/bids``."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    item_id: int = Field(..., ge=1, description="Item the bid is set for.")
    current_bid: Money = Field(..., description="Seller's current bid.")
    recommended: Money | None = Field(
        default=None, description="Server-recommended bid, when surfaced."
    )


class BbipOrder(BaseModel):
    """BBIP (budget-bound item promotion) order receipt."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    id: str = Field(..., description="BBIP order id.")
    budget: Money = Field(..., description="Allocated budget.")
    created_at: datetime = Field(..., description="Creation timestamp (UTC).")


class BbipForecast(BaseModel):
    """BBIP forecast envelope from ``GET /promotion/v1/items/services/bbip/budget/forecast``."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    min_bid: Money = Field(..., description="Minimum acceptable bid for this category/window.")
    recommended_bid: Money = Field(..., description="Server's recommended bid.")
    expected_views: int = Field(..., ge=0, description="Forecast views at the recommended bid.")


class PromotionList(RootModel[list[Promotion]]):
    """Top-level array envelope for the active-promotions response."""

    root: list[Promotion] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class BidList(RootModel[list[Bid]]):
    """Top-level array envelope for the bids response."""

    root: list[Bid] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)
