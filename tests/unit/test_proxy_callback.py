"""Unit tests for :class:`CallbackProxyTransport`."""
from __future__ import annotations

import pytest
from avitoapi import KEEP, CallbackProxyTransport, ProxyContext, parse_proxy
from avitoapi.exceptions import ProxyConnectionError


async def test_callback_called_on_acquire():
    seen: list[str] = []

    def get_next(ctx: ProxyContext):
        seen.append(ctx.reason)
        return "1.2.3.4:8080"

    transport = CallbackProxyTransport(get_next)
    async with transport.acquire() as proxy:
        assert proxy is not None
        assert "1.2.3.4:8080" in str(proxy.url)
    assert seen == ["acquire"]


async def test_keep_keeps_current_proxy():
    calls = {"n": 0}

    def get_next(ctx: ProxyContext):
        calls["n"] += 1
        if ctx.current is None:
            return "1.2.3.4:8080"
        return KEEP

    transport = CallbackProxyTransport(get_next)
    for _ in range(3):
        async with transport.acquire() as proxy:
            assert proxy is not None
            assert "1.2.3.4:8080" in str(proxy.url)
    assert calls["n"] == 3


async def test_callback_invoked_on_error_with_metadata():
    captured: list[ProxyContext] = []

    def get_next(ctx: ProxyContext):
        captured.append(ctx)
        return "1.2.3.4:8080" if ctx.current is None else "5.6.7.8:9090"

    transport = CallbackProxyTransport(get_next)
    acquire = transport.acquire()
    async with acquire:
        acquire.mark_invalid(ProxyConnectionError("boom"))

    # First call was for "acquire", second for "error".
    assert [c.reason for c in captured] == ["acquire", "error"]
    error_ctx = captured[1]
    assert error_ctx.total_errors == 1
    assert isinstance(error_ctx.last_error, ProxyConnectionError)
    assert error_ctx.current_errors == 1
    assert error_ctx.last_error_at > 0


async def test_initial_proxy_seeds_context():
    seen_current = []

    def get_next(ctx: ProxyContext):
        seen_current.append(ctx.current)
        return KEEP

    transport = CallbackProxyTransport(get_next, initial="10.0.0.1:8000")
    async with transport.acquire() as proxy:
        assert proxy is not None
    assert seen_current[0] is not None
    assert "10.0.0.1:8000" in str(seen_current[0].url)


async def test_set_current_overrides_callback_state():
    def get_next(ctx: ProxyContext):
        return KEEP

    transport = CallbackProxyTransport(get_next, initial="10.0.0.1:8000")
    transport.set_current(parse_proxy("9.9.9.9:1234"))
    async with transport.acquire() as proxy:
        assert proxy is not None
        assert "9.9.9.9:1234" in str(proxy.url)


async def test_async_callback_raises_helpful_error():
    async def async_get_next(ctx: ProxyContext):
        return "1.2.3.4:8080"

    transport = CallbackProxyTransport(async_get_next)  # type: ignore[arg-type]
    with pytest.raises(TypeError) as exc:
        transport.acquire()
    assert "synchronous" in str(exc.value).lower()
