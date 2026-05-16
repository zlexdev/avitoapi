"""Unit tests for the auction (CPA bids) domain."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from avitoapi.client import Client
from avitoapi.config import ClientConfig
from avitoapi.methods.auction import GetAuctionBids, SetAuctionBids
from avitoapi.models.auction import AuctionBid, AuctionBidList, SetAuctionBidsResult
from avitoapi.storage.memory import MemoryStorage

from tests._fake_session import FakeSession

FIXTURES = Path(__file__).parent.parent / "fixtures" / "auction"


def _load(name: str) -> dict[str, Any] | list[Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture
def auc_config() -> ClientConfig:
    return ClientConfig(
        client_id="cid",
        client_secret="secret",
        max_retries=0,
        backoff_initial_s=0.001,
        backoff_max_s=0.01,
    )


@pytest.fixture
async def auc_client(auc_config: ClientConfig) -> Any:
    session = FakeSession(config=auc_config)
    storage = MemoryStorage()
    session.register_route(
        "POST",
        "/token",
        body={"access_token": "tok", "token_type": "Bearer", "expires_in": 3600},
    )
    client = Client(config=auc_config, session=session, storage=storage)
    yield client, session
    await client.close()


async def test_get_auction_bids_returns_envelope(auc_client: tuple[Client, FakeSession]) -> None:
    client, session = auc_client
    session.register(GetAuctionBids, body=_load("bids_get.json"))

    bids = await client(GetAuctionBids())

    assert isinstance(bids, AuctionBidList)
    assert len(bids) == 2
    rows = list(bids)
    assert rows[0].category_id == 9
    assert rows[0].region_id == 637640
    assert rows[0].bid == 150
    sent = session.sent[-1]
    assert sent.http_method == "GET"
    assert sent.url.endswith("/auction/1/bids")


async def test_set_auction_bids_posts_and_is_idempotent(auc_client: tuple[Client, FakeSession]) -> None:
    client, session = auc_client
    session.register(SetAuctionBids, body=_load("bids_set.json"))

    payload = [
        AuctionBid(categoryId=9, regionId=637640, bid=200, maxBid=300),
        AuctionBid(categoryId=11, regionId=None, bid=100, maxBid=None),
    ]
    result = await client(SetAuctionBids(bids=payload))

    assert isinstance(result, SetAuctionBidsResult)
    assert result.updated == 2
    sent = session.sent[-1]
    assert sent.http_method == "POST"
    assert sent.url.endswith("/auction/1/bids")
    assert sent.body is not None
    assert "bids" in sent.body
    assert len(sent.body["bids"]) == 2
    assert "Idempotency-Key" in sent.headers
