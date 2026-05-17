"""Realty / short-term-rent domain — bookings, calendars, period prices.

Avito's STR (short-term-rent) surface follows the same wire shape as the rest
of the partner API: REST + JSON envelopes. The only domain-specific quirk is
that the calendar endpoint returns a ``date -> status`` map keyed by
``YYYY-MM-DD`` strings, which we eagerly coerce into ``date`` keys on the
:class:`Calendar` model.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator

from .common import Money


class BookingStatus(StrEnum):
    """Lifecycle state of one realty booking."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Booking(BaseModel):
    """One realty booking row (returned by both ``/realty`` and ``/core`` endpoints)."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    id: str = Field(..., description="Booking identifier (string).")
    item_id: int = Field(..., description="Avito item id of the booked listing.")
    guest_name: str | None = Field(default=None, description="Guest display name when surfaced.")
    check_in: date = Field(..., description="Check-in date (inclusive).")
    check_out: date = Field(..., description="Check-out date (exclusive).")
    status: BookingStatus = Field(..., description="Booking lifecycle state.")
    total: Money | None = Field(
        default=None,
        description="Total amount the guest will pay; absent when Avito omits the price.",
    )


class Calendar(BaseModel):
    """Availability calendar for one item.

    Wire shape: ``{"item_id": ..., "dates": {"YYYY-MM-DD": "<status>", ...}}``.
    The validator coerces string keys to ``date`` objects so callers don't have
    to re-parse.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    item_id: int = Field(..., description="Avito item id the calendar belongs to.")
    dates: dict[date, BookingStatus] = Field(
        default_factory=dict,
        description="Date-to-status map; only days Avito surfaces are present.",
    )

    @model_validator(mode="before")
    @classmethod
    def _coerce_date_keys(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        raw = value.get("dates")
        if not isinstance(raw, dict):
            return value
        coerced: dict[Any, Any] = {}
        for key, status in raw.items():
            if isinstance(key, str):
                try:
                    coerced[date.fromisoformat(key)] = status
                    continue
                except ValueError:
                    pass
            coerced[key] = status
        return {**value, "dates": coerced}


class PeriodPrice(BaseModel):
    """One pricing rule over a date range for an item.

    ``date_to`` is inclusive in Avito's convention (matches the booking
    semantics where ``check_out`` is exclusive but pricing windows are
    inclusive — Avito's documented quirk).
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    date_from: date = Field(..., description="Window start (inclusive).")
    date_to: date = Field(..., description="Window end (inclusive).")
    price: Money = Field(..., description="Per-night price for the window.")


class BookingList(RootModel[list[Booking]]):
    """Top-level JSON array envelope for booking-list endpoints."""

    root: list[Booking] = Field(default_factory=list)

    def __iter__(self) -> Iterator[Booking]:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class PeriodPriceList(RootModel[list[PeriodPrice]]):
    """Top-level JSON array envelope for ``GET /realty/v1/items/{item_id}/period_prices``.

    Doubles as the request body shape for ``PUT .../period_prices`` — Avito
    accepts the same JSON array on both directions, so callers construct one
    list and the method-class serialises it the right way.
    """

    root: list[PeriodPrice] = Field(default_factory=list)

    def __iter__(self) -> Iterator[PeriodPrice]:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)
