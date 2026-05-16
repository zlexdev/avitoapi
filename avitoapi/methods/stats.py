"""Stats-domain endpoints — shallow / deep item stats, call stats, spendings."""
from __future__ import annotations

from datetime import date, datetime
from typing import ClassVar, Self

from pydantic import Field, field_validator, model_validator

from ..models.balance import OperationList
from ..models.stats import CallStatList, ItemViewStatsList
from ._base import BaseMethod

_SHALLOW_MAX_IDS = 200
_SHALLOW_MAX_WINDOW_DAYS = 270


class ItemStatsShallow(BaseMethod[ItemViewStatsList]):
    """Bulk shallow per-item stats via ``GET /stats/v1/accounts/{user_id}/items/shallow``.

    Avito documents hard caps: ≤200 item ids per request, ≤270-day window.
    Both are validated client-side so callers don't waste a round-trip on a 4xx.
    """

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/stats/v1/accounts/{user_id}/items/shallow"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id"})

    user_id: int = Field(..., ge=1)
    item_ids: list[int] = Field(..., min_length=1)
    date_from: date = Field(..., description="Window start (inclusive).")
    date_to: date = Field(..., description="Window end (inclusive).")

    @field_validator("item_ids")
    @classmethod
    def _cap_ids(cls, value: list[int]) -> list[int]:
        if len(value) > _SHALLOW_MAX_IDS:
            raise ValueError(
                f"item_ids: Avito caps shallow stats at {_SHALLOW_MAX_IDS} ids per request",
            )
        return value

    @model_validator(mode="after")
    def _check_window(self) -> Self:
        delta = (self.date_to - self.date_from).days
        if delta < 0:
            raise ValueError("date_to must not precede date_from")
        if delta > _SHALLOW_MAX_WINDOW_DAYS:
            raise ValueError(
                f"date range {delta}d exceeds Avito's {_SHALLOW_MAX_WINDOW_DAYS}d limit",
            )
        return self


class ItemStatsDeep(BaseMethod[ItemViewStatsList]):
    """Deep per-item stats via ``POST /stats/v1/accounts/{user_id}/items``.

    Body carries date range, item ids, and the subset of fields to fetch.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/stats/v1/accounts/{user_id}/items"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id"})

    user_id: int = Field(..., ge=1)
    item_ids: list[int] = Field(..., min_length=1)
    date_from: date = Field(...)
    date_to: date = Field(...)
    fields: list[str] = Field(
        default_factory=lambda: ["views", "contacts", "favorites"],
        description="Stats columns to return; defaults to the common triple.",
    )


class CallStats(BaseMethod[CallStatList]):
    """Per-item call stats via ``GET /stats/v1/accounts/{user_id}/items/{item_id}/calls``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/stats/v1/accounts/{user_id}/items/{item_id}/calls"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id", "item_id"})

    user_id: int = Field(..., ge=1)
    item_id: int = Field(..., ge=1)


class Spendings(BaseMethod[OperationList]):
    """Profile spendings via ``POST /stats/v2/accounts/{user_id}/spendings``.

    Returns the raw operation list (one element per spending event in the window).
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/stats/v2/accounts/{user_id}/spendings"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id"})

    user_id: int = Field(..., ge=1)
    date_from: datetime = Field(...)
    date_to: datetime = Field(...)
