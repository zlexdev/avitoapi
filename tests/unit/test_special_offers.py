"""Unit tests for the special-offers (SBC gateway) domain."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from avitoapi.client import Client
from avitoapi.config import ClientConfig
from avitoapi.methods.special_offers import (
    GetAvailableOffers,
    GetOffersStats,
    GetOfferTariffInfo,
    MultiConfirmOffers,
    MultiCreateOffers,
    OfferDraft,
)
from avitoapi.models.special_offers import (
    AvailableOfferList,
    OfferConfirmationList,
    OfferCreateResultList,
    OfferStatList,
    OfferTariffInfo,
)
from avitoapi.storage.memory import MemoryStorage

from tests._fake_session import FakeSession

FIXTURES = Path(__file__).parent.parent / "fixtures" / "special_offers"


def _load(name: str) -> dict[str, Any] | list[Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture
def so_config() -> ClientConfig:
    return ClientConfig(
        client_id="cid",
        client_secret="secret",
        max_retries=0,
        backoff_initial_s=0.001,
        backoff_max_s=0.01,
    )


@pytest.fixture
async def so_client(so_config: ClientConfig) -> Any:
    session = FakeSession(config=so_config)
    storage = MemoryStorage()
    session.register_route(
        "POST",
        "/token",
        body={"access_token": "tok", "token_type": "Bearer", "expires_in": 3600},
    )
    client = Client(config=so_config, session=session, storage=storage)
    yield client, session
    await client.close()


async def test_get_available_offers_posts_item_ids(
    so_client: tuple[Client, FakeSession],
) -> None:
    client, session = so_client
    session.register(GetAvailableOffers, body=_load("available.json"))

    slots = await client(GetAvailableOffers(item_ids=[4001, 4002]))

    assert isinstance(slots, AvailableOfferList)
    assert len(slots) == 2
    rows = list(slots)
    assert rows[0].item_id == 4001
    assert rows[0].max_discount_percent == 30
    sent = session.sent[-1]
    assert sent.http_method == "POST"
    assert sent.url.endswith("/special-offers/v1/available")
    assert sent.body is not None
    assert sent.body.get("item_ids") == [4001, 4002]


async def test_multi_create_offers_is_idempotent(
    so_client: tuple[Client, FakeSession],
) -> None:
    client, session = so_client
    session.register(MultiCreateOffers, body=_load("multi_create.json"))

    drafts = [
        OfferDraft(itemId=4001, chatId="u2i-aaa", discountPercent=10),
        OfferDraft(itemId=4002, chatId=None, discountPercent=15),
    ]
    result = await client(MultiCreateOffers(offers=drafts))

    assert isinstance(result, OfferCreateResultList)
    assert len(result) == 2
    sent = session.sent[-1]
    assert sent.http_method == "POST"
    assert sent.url.endswith("/special-offers/v1/multiCreate")
    assert "Idempotency-Key" in sent.headers


async def test_multi_confirm_offers_returns_per_row_outcome(
    so_client: tuple[Client, FakeSession],
) -> None:
    client, session = so_client
    session.register(MultiConfirmOffers, body=_load("multi_confirm.json"))

    result = await client(MultiConfirmOffers(offer_ids=["off-001", "off-002"]))

    assert isinstance(result, OfferConfirmationList)
    rows = list(result)
    assert rows[0].confirmed is True
    assert rows[1].confirmed is False
    assert rows[1].error == "discount exceeds cap"
    sent = session.sent[-1]
    assert sent.http_method == "POST"
    assert "Idempotency-Key" in sent.headers


async def test_get_offers_stats_decodes_envelope(
    so_client: tuple[Client, FakeSession],
) -> None:
    client, session = so_client
    session.register(GetOffersStats, body=_load("stats.json"))

    stats = await client(GetOffersStats(offer_ids=["off-001"]))

    assert isinstance(stats, OfferStatList)
    rows = list(stats)
    assert rows[0].sent == 100
    assert rows[0].accepted == 12


async def test_get_offer_tariff_info_decodes(
    so_client: tuple[Client, FakeSession],
) -> None:
    client, session = so_client
    session.register(GetOfferTariffInfo, body=_load("tariff_info.json"))

    info = await client(GetOfferTariffInfo())

    assert isinstance(info, OfferTariffInfo)
    assert info.daily_limit == 200
    assert info.used_today == 18
    sent = session.sent[-1]
    assert sent.http_method == "POST"
    assert sent.url.endswith("/special-offers/v1/tariffInfo")
