"""Unit tests for the stock-management domain."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from avitoapi.client import Client
from avitoapi.config import ClientConfig
from avitoapi.methods.stock_management import GetStockInfo, UpdateStocks
from avitoapi.models.stock_management import StockInfo, StockInfoList, StockUpdateResult
from avitoapi.storage.memory import MemoryStorage

from tests._fake_session import FakeSession

FIXTURES = Path(__file__).parent.parent / "fixtures" / "stock_management"


def _load(name: str) -> dict[str, Any] | list[Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture
def sm_config() -> ClientConfig:
    return ClientConfig(
        client_id="cid",
        client_secret="secret",
        max_retries=0,
        backoff_initial_s=0.001,
        backoff_max_s=0.01,
    )


@pytest.fixture
async def sm_client(sm_config: ClientConfig) -> Any:
    session = FakeSession(config=sm_config)
    storage = MemoryStorage()
    session.register_route(
        "POST",
        "/token",
        body={"access_token": "tok", "token_type": "Bearer", "expires_in": 3600},
    )
    client = Client(config=sm_config, session=session, storage=storage)
    yield client, session
    await client.close()


async def test_get_stock_info_posts_item_ids(sm_client: tuple[Client, FakeSession]) -> None:
    client, session = sm_client
    session.register(GetStockInfo, body=_load("stock_info.json"))

    info = await client(GetStockInfo(item_ids=[1001, 1002]))

    assert isinstance(info, StockInfoList)
    assert len(info) == 2
    rows = list(info)
    assert rows[0].item_id == 1001
    assert rows[0].in_stock == 12
    sent = session.sent[-1]
    assert sent.http_method == "POST"
    assert sent.url.endswith("/stock-management/1/info")
    assert sent.body is not None
    assert sent.body.get("item_ids") == [1001, 1002]


async def test_update_stocks_is_put_and_idempotent(sm_client: tuple[Client, FakeSession]) -> None:
    client, session = sm_client
    session.register(UpdateStocks, body=_load("stock_update.json"))

    payload = [
        StockInfo(itemId=1001, warehouseId="wh-main", inStock=20, reserved=1),
        StockInfo(itemId=1002, warehouseId="wh-main", inStock=5, reserved=0),
    ]
    result = await client(UpdateStocks(stocks=payload))

    assert isinstance(result, StockUpdateResult)
    assert result.updated == 2
    sent = session.sent[-1]
    assert sent.http_method == "PUT"
    assert sent.url.endswith("/stock-management/1/stocks")
    assert sent.body is not None
    assert "stocks" in sent.body
    assert len(sent.body["stocks"]) == 2
    assert "Idempotency-Key" in sent.headers
