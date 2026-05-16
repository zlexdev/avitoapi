"""Unit tests for :class:`HMACSignatureMiddleware`."""
from __future__ import annotations

import hashlib
import hmac

import pytest
from avitoapi.web.middlewares.hmac_signature import (
    HMACSignatureMiddleware,
    HMACSignatureMissingError,
)


def _sign(body: bytes, secret: str) -> str:
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


async def test_correct_signature_accepts():
    secret = "shh"

    async def provider(_id: str) -> str:
        return secret

    mw = HMACSignatureMiddleware(provider)
    body = b'{"hello":"world"}'
    sig = _sign(body, secret)
    assert await mw.verify(body, sig, "webhook-1") is True


async def test_wrong_signature_rejects():
    async def provider(_id: str) -> str:
        return "shh"

    mw = HMACSignatureMiddleware(provider)
    body = b'{"hello":"world"}'
    assert await mw.verify(body, "deadbeef", "webhook-1") is False


async def test_unknown_webhook_id_rejects():
    async def provider(_id: str) -> str | None:
        return None

    mw = HMACSignatureMiddleware(provider)
    body = b"x"
    sig = _sign(body, "anything")
    assert await mw.verify(body, sig, "unknown") is False


async def test_missing_signature_required_raises():
    async def provider(_id: str) -> str:
        return "shh"

    mw = HMACSignatureMiddleware(provider, require_signature=True)
    with pytest.raises(HMACSignatureMissingError):
        await mw.verify(b"x", None, "webhook-1")
    with pytest.raises(HMACSignatureMissingError):
        await mw.verify(b"x", "", "webhook-1")


async def test_missing_signature_optional_returns_false():
    async def provider(_id: str) -> str:
        return "shh"

    mw = HMACSignatureMiddleware(provider, require_signature=False)
    assert await mw.verify(b"x", None, "webhook-1") is False
    assert await mw.verify(b"x", "", "webhook-1") is False


async def test_constant_time_compare_used():
    """Sanity: middleware uses ``hmac.compare_digest`` (no early-return on length).

    We can't directly measure timing, but we can verify two equal-length wrong
    sigs are uniformly rejected.
    """
    async def provider(_id: str) -> str:
        return "secret"

    mw = HMACSignatureMiddleware(provider)
    body = b"payload"
    real = _sign(body, "secret")
    wrong_same_len = "0" * len(real)
    assert await mw.verify(body, real, "id") is True
    assert await mw.verify(body, wrong_same_len, "id") is False
