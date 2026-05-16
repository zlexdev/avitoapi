"""Promotion v1 — active promotions, drop, bids, BBIP order + forecast."""
from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..models.promotion import BbipForecast as BbipForecastModel
from ..models.promotion import BbipOrder, BidList, PromotionList
from ._base import BaseMethod


class ListActivePromotions(BaseMethod[PromotionList]):
    """List currently active promotions via ``GET /promotion/v1/items``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/promotion/v1/items"

    item_ids: list[int] | None = Field(
        default=None,
        description="Optional subset of item ids to query.",
    )


class DropPromotion(BaseMethod[None]):
    """Drop the active promotion(s) via ``DELETE /promotion/v1/items``.

    The body carries the item ids to drop.
    """

    __http_method__: ClassVar[str] = "DELETE"
    __endpoint__: ClassVar[str] = "/promotion/v1/items"
    __body_fields__: ClassVar[frozenset[str] | None] = frozenset({"item_ids"})

    item_ids: list[int] = Field(..., min_length=1)


class ListBids(BaseMethod[BidList]):
    """List current bids via ``GET /promotion/v1/items/bids``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/promotion/v1/items/bids"

    item_ids: list[int] | None = Field(
        default=None,
        description="Optional subset of item ids to query.",
    )


class CreateBbipOrder(BaseMethod[BbipOrder]):
    """Create a BBIP order via ``PUT /promotion/v1/items/services/bbip/orders/create``."""

    __http_method__: ClassVar[str] = "PUT"
    __endpoint__: ClassVar[str] = "/promotion/v1/items/services/bbip/orders/create"
    __idempotent_mutation__: ClassVar[bool] = True

    item_ids: list[int] = Field(..., min_length=1)
    budget: int = Field(..., ge=1, description="Daily / total budget in integer rubles.")


class BbipForecast(BaseMethod[BbipForecastModel]):
    """BBIP forecast via ``GET /promotion/v1/items/services/bbip/budget/forecast``.

    Method-class shares the name with its return model; reach the DTO via
    ``avitoapi.models.promotion.BbipForecast`` if you need to disambiguate.
    """

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/promotion/v1/items/services/bbip/budget/forecast"

    item_id: int = Field(..., ge=1)
