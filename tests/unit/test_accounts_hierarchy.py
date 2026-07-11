"""Unit tests for the accounts-hierarchy domain."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from avitoapi.client import Client
from avitoapi.config import ClientConfig
from avitoapi.methods.accounts_hierarchy import (
    CheckAhUserV1,
    GetEmployeesV1,
    LinkItemsV1,
    ListCompanyPhonesV1,
    ListItemsByEmployeeIdV1,
)
from avitoapi.models.accounts_hierarchy import (
    CheckAhUserV1Response,
    CompanyPhonesResult,
    GetEmployeesResult,
    ListItemsByEmployeeIdResult,
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
    session.register(CheckAhUserV1, body=_load("check_ah_user.json"))

    status = await client(CheckAhUserV1())

    assert isinstance(status, CheckAhUserV1Response)
    assert status.is_employee is True
    assert status.avito_company_id == 99001
    sent = session.sent[-1]
    assert sent.http_method == "GET"
    assert sent.url.endswith("/checkAhUserV1")


async def test_get_employees_returns_envelope(ah_client: tuple[Client, FakeSession]) -> None:
    client, session = ah_client
    session.register(GetEmployeesV1, body=_load("employees.json"))

    employees = await client(GetEmployeesV1())

    assert isinstance(employees, GetEmployeesResult)
    rows = employees.root
    assert len(rows) == 2
    assert rows[0].employee_id == 101
    assert rows[1].name == "Bob Employee"


async def test_link_items_posts_body(ah_client: tuple[Client, FakeSession]) -> None:
    client, session = ah_client
    session.register(LinkItemsV1, body=_load("link_items.json"))

    result = await client(LinkItemsV1(employee_id=101, item_ids=[5001, 5002, 5003]))

    assert result is None
    sent = session.sent[-1]
    assert sent.http_method == "POST"
    assert sent.url.endswith("/linkItemsV1")
    assert sent.body is not None
    assert sent.body.get("employeeId") == 101
    assert sent.body.get("itemIds") == [5001, 5002, 5003]


async def test_list_company_phones_decodes_envelope(ah_client: tuple[Client, FakeSession]) -> None:
    client, session = ah_client
    session.register(ListCompanyPhonesV1, body=_load("phones.json"))

    phones = await client(ListCompanyPhonesV1())

    assert isinstance(phones, CompanyPhonesResult)
    assert phones.result is not None
    assert phones.result.phones == ["+74950000001", "+74950000002"]


async def test_list_items_by_employee_posts_body(ah_client: tuple[Client, FakeSession]) -> None:
    client, session = ah_client
    session.register(ListItemsByEmployeeIdV1, body=_load("employee_items.json"))

    items = await client(ListItemsByEmployeeIdV1(category_id=24, employee_id=101))

    assert isinstance(items, ListItemsByEmployeeIdResult)
    assert items.has_next is False
    assert items.items == [5001, 5002]
    sent = session.sent[-1]
    assert sent.http_method == "POST"
    assert sent.url.endswith("/listItemsByEmployeeIdV1")
    assert sent.body is not None
    assert sent.body.get("employeeId") == 101
    assert sent.body.get("categoryId") == 24
