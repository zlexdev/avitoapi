"""Unit tests for ``ProxyErrorMiddleware`` and ``RetryMiddleware``."""
from __future__ import annotations

import pytest
from avitoapi import ProxyErrorMiddleware, RetryMiddleware
from avitoapi.exceptions import (
    ConnectionError as SDKConnectionError,
)
from avitoapi.exceptions import (
    ProxyBanned,
    ProxyConnectionError,
    ProxyError,
)
from avitoapi.exceptions import (
    TimeoutError as SDKTimeoutError,
)
from avitoapi.sessions._models import PreparedRequest, RawResponse, RequestContext
from avitoapi.utils.proxy._base import Proxy, ProxyAcquireContext
from pydantic import AnyUrl


def _ctx_with_proxy() -> RequestContext:
    proxy = Proxy(url=AnyUrl("http://1.2.3.4:8080"))
    ctx = RequestContext(client=None)
    ctx.proxy = proxy
    ctx.proxy_acquire = ProxyAcquireContext(proxy=proxy)
    return ctx


async def test_proxy_error_middleware_translates_connection_error():
    mw = ProxyErrorMiddleware()
    ctx = _ctx_with_proxy()
    prepared = PreparedRequest(host="www", http_method="GET", url="/x")

    async def _failing(_prep, _ctx):
        raise SDKConnectionError("conn refused")

    with pytest.raises(ProxyConnectionError) as exc:
        await mw(_failing, prepared, ctx)
    assert "conn refused" in str(exc.value)
    assert ctx.proxy_acquire is not None
    assert ctx.proxy_acquire.invalid


async def test_proxy_error_middleware_translates_timeout():
    mw = ProxyErrorMiddleware()
    ctx = _ctx_with_proxy()
    prepared = PreparedRequest(host="www", http_method="GET", url="/x")

    async def _failing(_prep, _ctx):
        raise SDKTimeoutError("read timeout")

    with pytest.raises(ProxyError):
        await mw(_failing, prepared, ctx)


async def test_proxy_error_middleware_passes_through_without_proxy():
    mw = ProxyErrorMiddleware()
    ctx = RequestContext(client=None)  # no proxy bound
    prepared = PreparedRequest(host="www", http_method="GET", url="/x")

    async def _failing(_prep, _ctx):
        raise SDKConnectionError("conn refused")

    with pytest.raises(SDKConnectionError):
        await mw(_failing, prepared, ctx)


async def test_retry_middleware_retries_proxy_error_until_max():
    mw = RetryMiddleware(max_retries=2, initial_s=0.001)
    ctx = _ctx_with_proxy()
    prepared = PreparedRequest(host="www", http_method="POST", url="/x")
    calls = {"n": 0}

    async def _failing(_prep, _ctx):
        calls["n"] += 1
        raise ProxyConnectionError("nope")

    with pytest.raises(ProxyConnectionError):
        await mw(_failing, prepared, ctx)
    assert calls["n"] == 3  # initial attempt + 2 retries


async def test_retry_middleware_gives_up_on_proxy_exhausted():
    mw = RetryMiddleware(max_retries=5, initial_s=0.001)
    ctx = _ctx_with_proxy()
    prepared = PreparedRequest(host="www", http_method="POST", url="/x")
    calls = {"n": 0}

    async def _failing(_prep, _ctx):
        calls["n"] += 1
        from avitoapi.exceptions import ProxyExhausted

        raise ProxyExhausted("nothing left")

    with pytest.raises(Exception):  # ProxyExhausted falls under give_up_on
        await mw(_failing, prepared, ctx)
    assert calls["n"] == 1


async def test_retry_middleware_does_not_retry_unknown_errors():
    mw = RetryMiddleware(max_retries=3, initial_s=0.001)
    ctx = _ctx_with_proxy()
    prepared = PreparedRequest(host="www", http_method="GET", url="/x")
    calls = {"n": 0}

    async def _failing(_prep, _ctx):
        calls["n"] += 1
        raise ValueError("not a proxy issue")

    with pytest.raises(ValueError):
        await mw(_failing, prepared, ctx)
    assert calls["n"] == 1


async def test_retry_middleware_returns_response_on_success():
    mw = RetryMiddleware(max_retries=2, initial_s=0.001)
    ctx = _ctx_with_proxy()
    prepared = PreparedRequest(host="www", http_method="GET", url="/x")
    expected = RawResponse(status=200, body=b"ok")

    async def _ok(_prep, _ctx):
        return expected

    response = await mw(_ok, prepared, ctx)
    assert response is expected


def test_proxy_banned_carries_failure_count():
    err = ProxyBanned("done", proxy_url="http://1.2.3.4:8080", failure_count=3)
    assert err.failure_count == 3
    assert err.proxy_url == "http://1.2.3.4:8080"
