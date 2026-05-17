"""Realty / short-term-rent — bookings, calendar, period prices."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from avitoapi.client import Client
from avitoapi.methods.realty import (
    GetCalendar,
    GetPeriodPrices,
    ItemBookings,
    ListBookings,
    UpdatePeriodPrices,
)
from avitoapi.models.common import Currency, Money
from avitoapi.models.realty import (
    BookingList,
    BookingStatus,
    Calendar,
    PeriodPrice,
    PeriodPriceList,
)

from tests._fake_session import FakeSession


async def test_list_bookings_returns_envelope_with_one_row(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ListBookings, "realty/bookings.json")

    envelope = await client(
        ListBookings(date_from=date(2026, 6, 1), date_to=date(2026, 6, 30)),
    )

    assert isinstance(envelope, BookingList)
    assert len(envelope) == 1
    rows = list(envelope)
    assert rows[0].status is BookingStatus.CONFIRMED
    assert rows[0].total is not None
    assert rows[0].total.amount == Decimal("12000")


async def test_get_calendar_coerces_date_keys(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetCalendar, "realty/calendar.json")

    cal = await client(GetCalendar(item_id=555))

    assert isinstance(cal, Calendar)
    assert cal.item_id == 555
    assert cal.dates[date(2026, 6, 1)] is BookingStatus.CONFIRMED
    assert cal.dates[date(2026, 6, 3)] is BookingStatus.PENDING


async def test_get_period_prices_returns_typed_envelope(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetPeriodPrices, "realty/period_prices.json")

    prices = await client(GetPeriodPrices(item_id=555))

    assert isinstance(prices, PeriodPriceList)
    assert len(prices) == 1
    assert list(prices)[0].price.amount == Decimal("3000")


async def test_update_period_prices_emits_put_with_idempotency_key(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.register(UpdatePeriodPrices, body=b"", status=204)

    await client(
        UpdatePeriodPrices(
            item_id=555,
            prices=[
                PeriodPrice(
                    date_from=date(2026, 6, 1),
                    date_to=date(2026, 6, 30),
                    price=Money(amount=Decimal("3000"), currency=Currency.RUB),
                ),
            ],
        ),
    )

    prepared = fake_session.sent[-1]
    assert prepared.http_method == "PUT"
    assert prepared.url.endswith("/realty/v1/items/555/period_prices")
    assert "Idempotency-Key" in prepared.headers


async def test_item_bookings_uses_path_template(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ItemBookings, "realty/bookings.json")

    envelope = await client(ItemBookings(user_id=42, item_id=555))

    assert isinstance(envelope, BookingList)
    prepared = fake_session.sent[-1]
    assert prepared.url.endswith("/core/v1/accounts/42/items/555/bookings")
