"""Promotion v1 — list / drop / bids / BBIP order / forecast round-trips."""

from __future__ import annotations

import json

from avitoapi.client import Client
from avitoapi.methods.promotion import (
    BbipForecast,
    CreateBbipOrder,
    DropPromotion,
    ListActivePromotions,
    ListBids,
)
from avitoapi.models.promotion import BbipForecast as BbipForecastModel
from avitoapi.models.promotion import BbipOrder, BidList, PromotionList

from tests._fake_session import FakeSession


async def test_list_active_promotions_decodes_list(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ListActivePromotions, "promotion/active_promotions.json")

    promos = await client(ListActivePromotions())

    assert isinstance(promos, PromotionList)
    assert len(promos) == 2
    assert promos.root[0].service == "premium"


async def test_drop_promotion_sends_body_with_item_ids(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.register(DropPromotion, body=b"", status=204)

    result = await client(DropPromotion(item_ids=[9001, 9002]))

    assert result is None
    prepared = fake_session.sent[-1]
    assert prepared.http_method == "DELETE"
    assert prepared.url.endswith("/promotion/v1/items")
    body = prepared.body if isinstance(prepared.body, dict) else json.loads(prepared.body)
    assert body["item_ids"] == [9001, 9002]


async def test_list_bids_decodes(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ListBids, "promotion/bids.json")

    bids = await client(ListBids())

    assert isinstance(bids, BidList)
    assert len(bids) == 1
    assert str(bids.root[0].current_bid.amount) == "50.00"


async def test_create_bbip_order_idempotent(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(CreateBbipOrder, "promotion/bbip_order.json")

    order = await client(CreateBbipOrder(item_ids=[9001, 9002], budget=5000))

    assert isinstance(order, BbipOrder)
    assert order.id == "bbip_xyz789"
    prepared = fake_session.sent[-1]
    assert "Idempotency-Key" in prepared.headers


async def test_bbip_forecast_decodes(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(BbipForecast, "promotion/bbip_forecast.json")

    forecast = await client(BbipForecast(item_id=9001))

    assert isinstance(forecast, BbipForecastModel)
    assert forecast.expected_views == 12500
    assert str(forecast.recommended_bid.amount) == "75.00"
