"""Unit tests for the realty-reports domain."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from avitoapi.client import Client
from avitoapi.config import ClientConfig
from avitoapi.methods.realty_reports import (
    CreateRealtyReport,
    GetMarketPriceCorrespondence,
)
from avitoapi.models.realty_reports import MarketPriceCorrespondence, RealtyReportTask
from avitoapi.storage.memory import MemoryStorage

from tests._fake_session import FakeSession

FIXTURES = Path(__file__).parent.parent / "fixtures" / "realty_reports"


def _load(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture
def rr_config() -> ClientConfig:
    return ClientConfig(
        client_id="cid",
        client_secret="secret",
        max_retries=0,
        backoff_initial_s=0.001,
        backoff_max_s=0.01,
    )


@pytest.fixture
async def rr_client(rr_config: ClientConfig) -> Any:
    session = FakeSession(config=rr_config)
    storage = MemoryStorage()
    session.register_route(
        "POST",
        "/token",
        body={"access_token": "tok", "token_type": "Bearer", "expires_in": 3600},
    )
    client = Client(config=rr_config, session=session, storage=storage)
    yield client, session
    await client.close()


async def test_market_price_correspondence_renders_two_path_fields(
    rr_client: tuple[Client, FakeSession],
) -> None:
    client, session = rr_client
    session.register(GetMarketPriceCorrespondence, body=_load("market_price.json"))

    result = await client(GetMarketPriceCorrespondence(itemId=7777, price=50000))

    assert isinstance(result, MarketPriceCorrespondence)
    assert result.item_id == 7777
    assert result.correspondence == "within"
    assert result.market_median == 48500
    sent = session.sent[-1]
    assert sent.http_method == "GET"
    assert sent.url.endswith("/realty/v1/marketPriceCorrespondence/7777/50000")


async def test_create_realty_report_returns_task_and_is_idempotent(
    rr_client: tuple[Client, FakeSession],
) -> None:
    client, session = rr_client
    session.register(CreateRealtyReport, body=_load("create_report.json"))

    task = await client(CreateRealtyReport(itemId=7777))

    assert isinstance(task, RealtyReportTask)
    assert task.task_id == "task-abc-001"
    assert task.state == "pending"
    sent = session.sent[-1]
    assert sent.http_method == "POST"
    assert sent.url.endswith("/realty/v1/report/create/7777")
    assert "Idempotency-Key" in sent.headers
