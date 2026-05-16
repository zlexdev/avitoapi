"""Unit tests for the accounts-hierarchy domain."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from avitoapi.client import Client
from avitoapi.config import ClientConfig
from avitoapi.methods.accounts_hierarchy import (
    CheckAhUser,
    GetEmployees,
    LinkItems,
    ListCompanyPhones,
    ListItemsByEmployee,
)
from avitoapi.models.accounts_hierarchy import (
    AhUserStatus,
    EmployeeList,
    ItemList,
    LinkItemsResult,
    PhoneList,
)
from avitoapi.storage.memory import MemoryStorage

from tests._fake_session import FakeSession

FIXTURES = Path(__file__).parent.parent / "fixtures" / "accounts_hierarchy"


def _load(name: str) -> dict[str, Any] | list[Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture
def ah_config() -> ClientConfig:
    return ClientConfig(
        client_id="cid",
        client_secret="secret",
        max_retries=0,
        backoff_initial_s=0.001,
        backoff_max_s=0.01,
    )


@pytest.fixture
async def ah_client(ah_config: ClientConfig) -> Any:
    session = FakeSession(config=ah_config)
    storage = MemoryStorage()
    session.register_route(
        "POST",
        "/token",
        body={"access_token": "tok", "token_type": "Bearer", "expires_in": 3600},
    )
    client = Client(config=ah_config, session=session, storage=storage)
    yield client, session
    await client.close()


async def test_check_ah_user_decodes_status(ah_client: tuple[Client, FakeSession]) -> None:
    client, session = ah_client
    session.register(CheckAhUser, body=_load("check_ah_user.json"))

    status = await client(CheckAhUser())

    assert isinstance(status, AhUserStatus)
    assert status.is_ah_user is True
    assert status.company_id == 99001
    sent = session.sent[-1]
    assert sent.http_method == "GET"
    assert sent.url.endswith("/checkAhUserV1")


async def test_get_employees_returns_envelope(ah_client: tuple[Client, FakeSession]) -> None:
    client, session = ah_client
    session.register(GetEmployees, body=_load("employees.json"))

    employees = await client(GetEmployees())

    assert isinstance(employees, EmployeeList)
    assert len(employees) == 2
    rows = list(employees)
    assert rows[0].id == 101
    assert rows[1].role == "employee"


async def test_link_items_posts_idempotent_body(ah_client: tuple[Client, FakeSession]) -> None:
    client, session = ah_client
    session.register(LinkItems, body=_load("link_items.json"))

    result = await client(LinkItems(employee_id=101, item_ids=[5001, 5002, 5003]))

    assert isinstance(result, LinkItemsResult)
    assert result.linked == 3
    sent = session.sent[-1]
    assert sent.http_method == "POST"
    assert sent.url.endswith("/linkItemsV1")
    assert sent.body is not None
    assert sent.body.get("employee_id") == 101
    assert sent.body.get("item_ids") == [5001, 5002, 5003]
    assert "Idempotency-Key" in sent.headers


async def test_list_company_phones_decodes_envelope(ah_client: tuple[Client, FakeSession]) -> None:
    client, session = ah_client
    session.register(ListCompanyPhones, body=_load("phones.json"))

    phones = await client(ListCompanyPhones())

    assert isinstance(phones, PhoneList)
    assert len(phones) == 2
    rows = list(phones)
    assert rows[0].phone == "+74950000001"
    assert rows[0].employee_id == 101


async def test_list_items_by_employee_posts_body(ah_client: tuple[Client, FakeSession]) -> None:
    client, session = ah_client
    session.register(ListItemsByEmployee, body=_load("employee_items.json"))

    items = await client(ListItemsByEmployee(employee_id=101, limit=50, offset=0))

    assert isinstance(items, ItemList)
    assert len(items) == 2
    sent = session.sent[-1]
    assert sent.http_method == "POST"
    assert sent.url.endswith("/listItemsByEmployeeIdV1")
    assert sent.body is not None
    assert sent.body.get("employee_id") == 101
    assert sent.body.get("limit") == 50
