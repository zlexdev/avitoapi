"""Unit tests for the tariff domain."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from avitoapi.client import Client
from avitoapi.config import ClientConfig
from avitoapi.methods.tariff import GetTariffInfo
from avitoapi.models.tariff import TariffInfo
from avitoapi.storage.memory import MemoryStorage

from tests._fake_session import FakeSession

FIXTURES = Path(__file__).parent.parent / "fixtures" / "tariff"


def _load(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture
def tr_config() -> ClientConfig:
    return ClientConfig(
        client_id="cid",
        client_secret="secret",
        max_retries=0,
        backoff_initial_s=0.001,
        backoff_max_s=0.01,
    )


@pytest.fixture
async def tr_client(tr_config: ClientConfig) -> Any:
    session = FakeSession(config=tr_config)
    storage = MemoryStorage()
    session.register_route(
        "POST",
        "/token",
        body={"access_token": "tok", "token_type": "Bearer", "expires_in": 3600},
    )
    client = Client(config=tr_config, session=session, storage=storage)
    yield client, session
    await client.close()


async def test_get_tariff_info_decodes_envelope(tr_client: tuple[Client, FakeSession]) -> None:
    client, session = tr_client
    session.register(GetTariffInfo, body=_load("info.json"))

    info = await client(GetTariffInfo())

    assert isinstance(info, TariffInfo)
    assert info.current is not None
    assert info.current.level == "premium_v3"
    assert info.current.is_active is True
    assert info.current.price is not None
    assert info.current.price.price == 990.0
    sent = session.sent[-1]
    assert sent.http_method == "GET"
    assert sent.url.endswith("/tariff/info/1")
