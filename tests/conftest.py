"""Shared pytest fixtures for the avitoapi unit suite.

Conventions:
- ``pytest-asyncio`` runs in ``mode=auto``; no need to decorate every async test.
- No real HTTP — every test gets a :class:`FakeSession` instance.
- Sample loaders read JSON from ``tests/fixtures/``.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Callable
from datetime import UTC
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio
from avitoapi.auth.oauth import (
    OAuthClient,
    OAuthInjectorMiddleware,
    Token,
    TokenCache,
)
from avitoapi.client import Client
from avitoapi.config import ClientConfig
from avitoapi.methods.user import GetUserInfoSelf
from avitoapi.storage.memory import MemoryStorage

from tests._fake_session import FIXTURE_DIR, FakeSession


pytest_plugins = ("pytest_asyncio",)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Run every async test under pytest-asyncio without the per-test decorator."""
    for item in items:
        if isinstance(item, pytest.Function):
            if pytest_asyncio.is_async_test(item):
                item.add_marker(pytest.mark.asyncio)


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return FIXTURE_DIR


@pytest.fixture(scope="session")
def load_fixture() -> Callable[[str], dict[str, Any]]:
    def _load(name: str) -> dict[str, Any]:
        path = FIXTURE_DIR / name
        return json.loads(path.read_bytes().decode())

    return _load


@pytest.fixture
def oauth_token_payload(load_fixture: Callable[[str], dict[str, Any]]) -> dict[str, Any]:
    return load_fixture("oauth_token.json")


@pytest.fixture
def oauth_token_expired_payload(load_fixture: Callable[[str], dict[str, Any]]) -> dict[str, Any]:
    return load_fixture("oauth_token_expired.json")


@pytest.fixture
def accounts_self_payload(load_fixture: Callable[[str], dict[str, Any]]) -> dict[str, Any]:
    return load_fixture("accounts_self.json")


@pytest.fixture
def client_config() -> ClientConfig:
    """Minimal valid config — no live secrets, just enough for the builder to construct."""
    return ClientConfig(
        client_id="test_client_id",
        client_secret="test_client_secret",
        max_retries=2,
        backoff_initial_s=0.001,
        backoff_max_s=0.01,
    )


@pytest.fixture
def storage() -> MemoryStorage:
    return MemoryStorage()


@pytest.fixture
def fake_session(client_config: ClientConfig) -> FakeSession:
    return FakeSession(config=client_config)


@pytest.fixture
def token_cache(storage: MemoryStorage) -> TokenCache:
    return TokenCache(storage=storage)


@pytest.fixture
def oauth_client(
    client_config: ClientConfig,
    fake_session: FakeSession,
    token_cache: TokenCache,
) -> OAuthClient:
    return OAuthClient(config=client_config, http=fake_session, cache=token_cache)


@pytest.fixture
def oauth_injector(oauth_client: OAuthClient) -> OAuthInjectorMiddleware:
    def cache_key_builder(client: Any) -> str:
        return f"oauth:{client.config.client_id}"

    return OAuthInjectorMiddleware(oauth=oauth_client, cache_key_builder=cache_key_builder)


@pytest_asyncio.fixture
async def client(
    client_config: ClientConfig,
    fake_session: FakeSession,
    storage: MemoryStorage,
    oauth_injector: OAuthInjectorMiddleware,
    accounts_self_payload: dict[str, Any],
    oauth_token_payload: dict[str, Any],
) -> AsyncIterator[Client]:
    """A fully-wired Client ready for ``async with`` usage.

    Pre-registers the OAuth token endpoint and the accounts-self fixture so
    most tests can just ``await client.user_info_self()`` without extra setup.
    """
    fake_session.register_route("POST", "/token", body=oauth_token_payload)
    fake_session.register_route("GET", "/token/", body=oauth_token_payload)
    fake_session.register(GetUserInfoSelf, body=accounts_self_payload)

    fake_session.request_middlewares.register(oauth_injector)

    async with Client(
        config=client_config,
        session=fake_session,
        storage=storage,
    ) as built:
        yield built


@pytest.fixture
def sample_token(oauth_token_payload: dict[str, Any]) -> Token:
    """A ready-to-use Token built from the canned OAuth fixture."""
    from datetime import datetime, timedelta

    expires_at = datetime.now(UTC) + timedelta(seconds=oauth_token_payload["expires_in"])
    return Token(
        access_token=oauth_token_payload["access_token"],
        token_type=oauth_token_payload["token_type"],
        expires_at=expires_at,
    )
