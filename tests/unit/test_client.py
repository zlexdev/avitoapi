"""Unit tests for ``avitoapi.Client`` — facade, lifecycle, ``__call__``, ``user_info_self``.

Coverage:
- ``Client.__call__(GetUserInfoSelf())`` returns a bound ``UserInfoSelf`` via the funnel.
- ``async with Client(...)`` opens + closes the session exactly once.
- ``client.user_info_self()`` returns ``UserInfoSelf`` with ``account._client is client``.
- 403 + token_expired during a call triggers re-auth + retry via the injector.
"""

from __future__ import annotations

from typing import Any

from avitoapi import Client
from avitoapi.config import ClientConfig
from avitoapi.methods.user import GetUserInfoSelf
from avitoapi.models.user import UserInfoSelf
from avitoapi.storage.memory import MemoryStorage

from tests._fake_session import FakeResponse, FakeSession


async def test_client_call_returns_account_when_invoked_with_get_self(
    client: Client,
) -> None:
    account = await client(GetUserInfoSelf())

    assert isinstance(account, UserInfoSelf)
    assert account.id == 12345
    assert account.name == "Test Seller"


async def test_client_call_binds_returned_model_to_self(
    client: Client,
) -> None:
    account = await client(GetUserInfoSelf())

    assert account._client is client


async def test_get_self_returns_account_with_expected_fields(
    client: Client,
    accounts_self_payload: dict[str, Any],
) -> None:
    account = await client.user_info_self()

    assert account.id == accounts_self_payload["id"]
    assert account.name == accounts_self_payload["name"]
    assert account.email == accounts_self_payload["email"]
    assert account.phone == accounts_self_payload["phone"]
    assert account.profile_url == accounts_self_payload["profile_url"]


async def test_get_self_returns_account_bound_to_client(
    client: Client,
) -> None:
    account = await client.user_info_self()

    assert account._client is client


async def test_client_async_with_opens_and_closes_session(
    client_config: ClientConfig,
    fake_session: FakeSession,
    accounts_self_payload: dict[str, Any],
) -> None:
    fake_session.register(GetUserInfoSelf, body=accounts_self_payload)
    state: dict[str, int] = {"opens": 0, "closes": 0}

    original_open = fake_session.open
    original_close = fake_session.close

    async def tracked_open() -> None:
        state["opens"] += 1
        await original_open()

    async def tracked_close() -> None:
        state["closes"] += 1
        await original_close()

    fake_session.open = tracked_open  # type: ignore[method-assign]
    fake_session.close = tracked_close  # type: ignore[method-assign]

    async with Client(
        config=client_config,
        session=fake_session,
        storage=MemoryStorage(),
    ) as built:
        assert built is not None

    assert state["opens"] == 1
    assert state["closes"] == 1


async def test_client_reauths_and_retries_when_call_returns_token_expired_403(
    client_config: ClientConfig,
    accounts_self_payload: dict[str, Any],
    oauth_token_payload: dict[str, Any],
    oauth_token_expired_payload: dict[str, Any],
) -> None:
    """End-to-end through the funnel: first call returns 403+token_expired,
    middleware refreshes the token, retries, second call succeeds."""
    from avitoapi.auth.oauth import (
        OAuthClient,
        OAuthInjectorMiddleware,
        TokenCache,
    )

    storage = MemoryStorage()
    fake = FakeSession(config=client_config)
    fake.register_route("POST", "/token", body=oauth_token_payload)

    attempts: dict[str, int] = {"n": 0}

    def get_self_responder(prepared: Any) -> FakeResponse:
        attempts["n"] += 1
        if attempts["n"] == 1:
            return FakeResponse(body=oauth_token_expired_payload, status=403)
        return FakeResponse(body=accounts_self_payload, status=200)

    fake.register_responder(GetUserInfoSelf, get_self_responder)

    cache = TokenCache(storage=storage)
    oauth = OAuthClient(config=client_config, http=fake, cache=cache)
    injector = OAuthInjectorMiddleware(
        oauth=oauth,
        cache_key_builder=lambda c: f"oauth:{c.config.client_id}",
    )
    fake.request_middlewares.register(injector)

    async with Client(config=client_config, session=fake, storage=storage) as client:
        account = await client.user_info_self()

    assert isinstance(account, UserInfoSelf)
    assert account.id == 12345
    assert attempts["n"] == 2
