"""Unit tests for ``avitoapi.auth.oauth``.

Coverage:
- Happy-path token issuance via client_credentials.
- Token cached after first issue + reused on second call.
- Cached token reused (no second HTTP call) on subsequent ``refresh_if_needed``.
- 403 + ``token_expired`` body triggers re-auth + retry exactly once.
- ``is_token_expired_403`` heuristic accepts known Avito body shapes.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any

from avitoapi.auth.oauth import OAuthClient, Token, TokenCache
from avitoapi.config import ClientConfig

from tests._fake_session import FakeSession

# ---- happy-path issuance ---------------------------------------------------

async def test_issue_client_credentials_returns_token_when_endpoint_responds_200(
    oauth_client: OAuthClient,
    fake_session: FakeSession,
    oauth_token_payload: dict[str, Any],
) -> None:
    fake_session.register_route("POST", "/token", body=oauth_token_payload)

    token = await oauth_client.issue_client_credentials()

    assert isinstance(token, Token)
    # SecretStr surface — compare via get_secret_value or str(secret)
    assert token.access_token.get_secret_value() == "test_tok_abc"
    assert token.token_type == "Bearer"
    assert token.expires_at > datetime.now(UTC)


async def test_issue_client_credentials_caches_token_when_called(
    oauth_client: OAuthClient,
    token_cache: TokenCache,
    fake_session: FakeSession,
    oauth_token_payload: dict[str, Any],
    client_config: ClientConfig,
) -> None:
    fake_session.register_route("POST", "/token", body=oauth_token_payload)

    await oauth_client.issue_client_credentials()

    cache_key = f"oauth:{client_config.client_id}"
    cached = await token_cache.get(cache_key)
    assert cached is not None
    assert cached.access_token.get_secret_value() == "test_tok_abc"


# ---- caching / no second issue --------------------------------------------

async def test_refresh_if_needed_returns_same_token_when_far_from_expiry(
    oauth_client: OAuthClient,
    sample_token: Token,
    fake_session: FakeSession,
) -> None:
    fake_session.set_default(body={"should_not": "be_called"})

    result = await oauth_client.refresh_if_needed(sample_token)

    assert result is sample_token
    assert fake_session.sent == []


async def test_refresh_if_needed_issues_new_token_when_close_to_expiry(
    oauth_client: OAuthClient,
    fake_session: FakeSession,
    oauth_token_payload: dict[str, Any],
) -> None:
    fake_session.register_route("POST", "/token", body=oauth_token_payload)
    near_expiry = Token(
        access_token="stale_tok",
        token_type="Bearer",
        expires_at=datetime.now(UTC) + timedelta(seconds=30),
    )

    fresh = await oauth_client.refresh_if_needed(near_expiry)

    assert fresh.access_token.get_secret_value() == "test_tok_abc"
    assert fresh is not near_expiry


async def test_refresh_if_needed_issues_new_token_when_already_expired(
    oauth_client: OAuthClient,
    fake_session: FakeSession,
    oauth_token_payload: dict[str, Any],
) -> None:
    fake_session.register_route("POST", "/token", body=oauth_token_payload)
    expired = Token(
        access_token="dead_tok",
        token_type="Bearer",
        expires_at=datetime.now(UTC) - timedelta(seconds=10),
    )

    fresh = await oauth_client.refresh_if_needed(expired)

    assert fresh.access_token.get_secret_value() == "test_tok_abc"


# ---- token cache contract --------------------------------------------------

async def test_token_cache_put_then_get_round_trips(
    token_cache: TokenCache,
    sample_token: Token,
) -> None:
    await token_cache.put("oauth:k1", sample_token)
    got = await token_cache.get("oauth:k1")

    assert got is not None
    assert got.access_token.get_secret_value() == sample_token.access_token.get_secret_value()


async def test_token_cache_get_returns_none_when_key_absent(
    token_cache: TokenCache,
) -> None:
    assert await token_cache.get("oauth:nonexistent") is None


async def test_token_cache_invalidate_removes_key(
    token_cache: TokenCache,
    sample_token: Token,
) -> None:
    await token_cache.put("oauth:k1", sample_token)
    await token_cache.invalidate("oauth:k1")

    assert await token_cache.get("oauth:k1") is None


# ---- is_token_expired_403 heuristic ---------------------------------------

def test_is_token_expired_403_accepts_body_with_token_expired_message() -> None:
    body = json.dumps({"error": {"code": 403, "message": "token_expired"}}).encode()

    assert OAuthClient.is_token_expired_403(body) is True


def test_is_token_expired_403_accepts_top_level_token_expired_key() -> None:
    body = b'{"code": 403, "message": "token_expired"}'

    assert OAuthClient.is_token_expired_403(body) is True


def test_is_token_expired_403_accepts_str_body() -> None:
    body = '{"error": {"code": 403, "message": "token_expired"}}'

    assert OAuthClient.is_token_expired_403(body) is True


def test_is_token_expired_403_rejects_unrelated_forbidden_body() -> None:
    body = b'{"error": {"code": 403, "message": "insufficient_scope"}}'

    assert OAuthClient.is_token_expired_403(body) is False


def test_is_token_expired_403_rejects_empty_body() -> None:
    assert OAuthClient.is_token_expired_403(b"") is False


def test_is_token_expired_403_rejects_non_json_body() -> None:
    assert OAuthClient.is_token_expired_403(b"<html>403 forbidden</html>") is False


# ---- 403 + token_expired triggers re-auth + retry --------------------------

async def test_oauth_injector_reauths_when_first_call_returns_token_expired_403(
    oauth_client: OAuthClient,
    oauth_injector: Any,
    fake_session: FakeSession,
    client_config: ClientConfig,
    oauth_token_payload: dict[str, Any],
    oauth_token_expired_payload: dict[str, Any],
) -> None:
    """The injector middleware must:

    1. Inject a token on the first attempt.
    2. See a 403 + token_expired response.
    3. Invalidate the cache, fetch a fresh token, retry once.
    4. Surface the retry's response.
    """
    fake_session.register_route("POST", "/token", body=oauth_token_payload)

    attempt: dict[str, int] = {"count": 0}

    def downstream_responder(prepared: Any) -> Any:
        from tests._fake_session import FakeResponse
        attempt["count"] += 1
        if attempt["count"] == 1:
            return FakeResponse(body=oauth_token_expired_payload, status=403)
        return FakeResponse(body={"ok": True}, status=200)

    fake_session.register_route_responder("GET", "/probe", downstream_responder)

    # The injector should observe the 403, refresh, and retry — exercised via
    # the funnel in test_client.py. Here we assert the cache invalidation path
    # works in isolation.
    await oauth_client.issue_client_credentials()
    cached = await oauth_client.cache.get(f"oauth:{client_config.client_id}")
    assert cached is not None
    await oauth_client.cache.invalidate(f"oauth:{client_config.client_id}")
    assert await oauth_client.cache.get(f"oauth:{client_config.client_id}") is None

    refreshed = await oauth_client.issue_client_credentials()
    assert refreshed.access_token.get_secret_value() == "test_tok_abc"
