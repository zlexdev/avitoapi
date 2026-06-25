"""Realty / short-term-rent endpoints — bookings, calendars, period prices.

Five method-classes. ``UpdatePeriodPrices`` is the only mutating one — it
accepts a :class:`PeriodPriceList` (round-trippable: same envelope returned
from the GET endpoint) and is marked idempotent.

``ListBookings`` and ``ItemBookings`` cover two overlapping endpoints in
Avito's wire (one under ``/realty``, one under ``/core``); the SDK exposes
both because callers consume them on different surfaces (admin dashboards vs
per-item drilldowns).
"""

from __future__ import annotations

from datetime import date
from typing import Any, ClassVar

from pydantic import Field

from ..models.realty import (
    BookingList,
    Calendar,
    PeriodPrice,
    PeriodPriceList,
)
from ._base import BaseMethod


class ListBookings(BaseMethod[BookingList]):
    """Bookings in a window via ``GET /realty/v1/bookings``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/realty/v1/bookings"

    date_from: date = Field(..., description="Window start (inclusive).")
    date_to: date = Field(..., description="Window end (inclusive).")


class GetCalendar(BaseMethod[Calendar]):
    """Availability calendar via ``GET /realty/v1/items/{item_id}/calendar``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/realty/v1/items/{item_id}/calendar"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"item_id"})

    item_id: int = Field(..., ge=1)


class GetPeriodPrices(BaseMethod[PeriodPriceList]):
    """Active period-price rules via ``GET /realty/v1/items/{item_id}/period_prices``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/realty/v1/items/{item_id}/period_prices"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"item_id"})

    item_id: int = Field(..., ge=1)


class UpdatePeriodPrices(BaseMethod[None]):
    """Replace period-price rules via ``PUT /realty/v1/items/{item_id}/period_prices``.

    Avito's wire accepts a bare JSON array; we declare the field as
    ``prices: list[PeriodPrice]`` and the protocol serialises it. The endpoint
    returns no body — :class:`BaseMethod` honours ``__returning__ = None``
    (no decode) and the awaited result is ``None``.

    Idempotent mutation — auto-injects ``Idempotency-Key`` so a retried
    rollout doesn't double-write.
    """

    __http_method__: ClassVar[str] = "PUT"
    __endpoint__: ClassVar[str] = "/realty/v1/items/{item_id}/period_prices"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"item_id"})
    __idempotent_mutation__: ClassVar[bool] = True

    item_id: int = Field(..., ge=1)
    prices: list[PeriodPrice] = Field(
        ...,
        description="Replacement set of period-price rules (full list, not a delta).",
    )

    def model_dump(self, *args: Any, **kwargs: Any) -> dict[str, Any]:  # typed-Any: pydantic model_dump override
        # Avito accepts a bare JSON array on this endpoint; the funnel
        # serialises whatever the protocol routes into ``body``. We keep
        # the standard dump shape and let the protocol wrap it.
        return super().model_dump(*args, **kwargs)


class ItemBookings(BaseMethod[BookingList]):
    """Bookings for one item via ``GET /core/v1/accounts/{user_id}/items/{item_id}/bookings``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/core/v1/accounts/{user_id}/items/{item_id}/bookings"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id", "item_id"})

    user_id: int = Field(..., ge=1)
    item_id: int = Field(..., ge=1)
