"""CpxPromo v1 — getBids / getPromotionsByItemIds / remove / setAuto / setManual."""

from __future__ import annotations

import json

from avitoapi.client import Client
from avitoapi.methods.cpxpromo import (
    GetCpxBids,
    GetCpxPromotionsByItems,
    RemoveCpxPromotion,
    SetCpxAutoPromotion,
    SetCpxManualPromotion,
)
from avitoapi.models.cpxpromo import (
    CpxActionResult,
    CpxBidList,
    CpxPromotion,
    CpxPromotionList,
    CpxPromotionStatus,
)

from tests._fake_session import FakeSession


async def test_get_cpx_bids_uses_path_template(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetCpxBids, "cpxpromo/bids.json")

    bids = await client(GetCpxBids(item_id=9001))

    assert isinstance(bids, CpxBidList)
    assert len(bids) == 2
    rows = list(bids)
    assert rows[0].current_bid == 50
    assert rows[0].recommended == 75
    prepared = fake_session.sent[-1]
    assert prepared.http_method == "GET"
    assert prepared.url.endswith("/cpxpromo/1/getBids/9001")


async def test_get_cpx_promotions_by_items_decodes_modes(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetCpxPromotionsByItems, "cpxpromo/promotions.json")

    promos = await client(GetCpxPromotionsByItems(item_ids=[9001, 9002, 9003]))

    assert isinstance(promos, CpxPromotionList)
    assert len(promos) == 3
    rows = list(promos)
    assert rows[0].mode is CpxPromotionStatus.AUTO
    assert rows[1].mode is CpxPromotionStatus.MANUAL
    assert rows[1].bid == 120
    assert rows[2].mode is CpxPromotionStatus.OFF
    prepared = fake_session.sent[-1]
    assert prepared.http_method == "POST"
    assert prepared.url.endswith("/cpxpromo/1/getPromotionsByItemIds")
    body = prepared.body if isinstance(prepared.body, dict) else json.loads(prepared.body)
    assert body["item_ids"] == [9001, 9002, 9003]


async def test_remove_cpx_promotion_idempotent(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(RemoveCpxPromotion, "cpxpromo/action_result.json")

    result = await client(RemoveCpxPromotion(item_ids=[9001, 9002]))

    assert isinstance(result, CpxActionResult)
    assert result.ok is True
    assert result.affected == [9001, 9002]
    prepared = fake_session.sent[-1]
    assert prepared.url.endswith("/cpxpromo/1/remove")
    assert "Idempotency-Key" in prepared.headers


async def test_set_cpx_auto_promotion_idempotent(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(SetCpxAutoPromotion, "cpxpromo/action_result.json")

    await client(SetCpxAutoPromotion(item_ids=[9001]))

    prepared = fake_session.sent[-1]
    assert prepared.url.endswith("/cpxpromo/1/setAuto")
    assert "Idempotency-Key" in prepared.headers
    body = prepared.body if isinstance(prepared.body, dict) else json.loads(prepared.body)
    assert body["item_ids"] == [9001]


async def test_set_cpx_manual_promotion_idempotent_carries_bid(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(SetCpxManualPromotion, "cpxpromo/action_result.json")

    await client(SetCpxManualPromotion(item_ids=[9001, 9002], bid=120))

    prepared = fake_session.sent[-1]
    assert prepared.url.endswith("/cpxpromo/1/setManual")
    assert "Idempotency-Key" in prepared.headers
    body = prepared.body if isinstance(prepared.body, dict) else json.loads(prepared.body)
    assert body["item_ids"] == [9001, 9002]
    assert body["bid"] == 120


async def test_cpx_promotion_bound_methods_target_correct_endpoints(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(SetCpxManualPromotion, "cpxpromo/action_result.json")

    promo = CpxPromotion(item_id=9001, mode=CpxPromotionStatus.AUTO).as_(client)
    set_call = promo.set_manual(bid=200)
    await set_call

    prepared = fake_session.sent[-1]
    assert prepared.url.endswith("/cpxpromo/1/setManual")
    body = prepared.body if isinstance(prepared.body, dict) else json.loads(prepared.body)
    assert body["item_ids"] == [9001]
    assert body["bid"] == 200
