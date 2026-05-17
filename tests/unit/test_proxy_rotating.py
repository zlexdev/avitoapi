"""Unit tests for :class:`ListProxyTransport` rotation + ban logic."""
from __future__ import annotations

import asyncio
import random

import pytest
from avitoapi import ListProxyTransport, ProxyBanned, RotationStrategy
from avitoapi.exceptions import (
    ProxyConnectionError,
    ProxyExhausted,
)


async def test_round_robin_cycles_through_pool():
    transport = ListProxyTransport(
        ["1.1.1.1:8080", "2.2.2.2:8080", "3.3.3.3:8080"],
        strategy=RotationStrategy.ROUND_ROBIN,
    )
    picked = []
    for _ in range(6):
        async with transport.acquire() as proxy:
            assert proxy is not None
            picked.append(str(proxy.url))
    # Two full laps means we should have seen every entry twice.
    assert len(set(picked)) == 3
    # Cursor advances strictly — no proxy is repeated back-to-back.
    for prev, curr in zip(picked, picked[1:], strict=False):
        assert prev != curr


async def test_mark_invalid_increments_failure_count():
    transport = ListProxyTransport(["1.1.1.1:8080"], max_failures=5, raise_on_ban=False)
    async with transport.acquire() as proxy:
        assert proxy is not None
        ctx = _last_context(transport)
        # The acquire context is referenced through the transport — we mark it
        # via the manager surface instead.
    # Verify by triggering a failure flow.
    acquire = transport.acquire()
    async with acquire as proxy:
        acquire.mark_invalid(ProxyConnectionError("boom"))
    assert transport._health[_only_key(transport)].failure_count == 1


async def test_ban_threshold_marks_proxy_unhealthy():
    transport = ListProxyTransport(
        ["1.1.1.1:8080"],
        max_failures=2,
        raise_on_ban=False,
    )
    for _ in range(2):
        acquire = transport.acquire()
        async with acquire:
            acquire.mark_invalid(ProxyConnectionError("boom"))
    health = transport._health[_only_key(transport)]
    assert health.banned is True


async def test_ban_raises_when_raise_on_ban_true():
    transport = ListProxyTransport(
        ["1.1.1.1:8080"],
        max_failures=2,
        raise_on_ban=True,
    )
    acquire = transport.acquire()
    async with acquire:
        acquire.mark_invalid(ProxyConnectionError("boom"))
    # Second failure crosses the threshold and surfaces ProxyBanned.
    with pytest.raises(ProxyBanned) as exc_info:
        acquire = transport.acquire()
        async with acquire:
            acquire.mark_invalid(ProxyConnectionError("boom-again"))
    assert exc_info.value.failure_count == 2
    assert "1.1.1.1:8080" in (exc_info.value.proxy_url or "")


async def test_pool_exhausted_when_every_proxy_banned():
    transport = ListProxyTransport(
        ["1.1.1.1:8080"],
        max_failures=1,
        raise_on_ban=False,
    )
    acquire = transport.acquire()
    async with acquire:
        acquire.mark_invalid(ProxyConnectionError("boom"))
    with pytest.raises(ProxyExhausted):
        transport.acquire()


async def test_cooldown_reactivates_banned_proxy():
    transport = ListProxyTransport(
        ["1.1.1.1:8080"],
        max_failures=1,
        cooldown_s=0.05,
        raise_on_ban=False,
    )
    acquire = transport.acquire()
    async with acquire:
        acquire.mark_invalid(ProxyConnectionError("boom"))
    assert transport.banned()
    await asyncio.sleep(0.06)
    assert transport.healthy()


async def test_random_strategy_uses_rng():
    rng = random.Random(42)
    transport = ListProxyTransport(
        ["1.1.1.1:8080", "2.2.2.2:8080", "3.3.3.3:8080"],
        strategy=RotationStrategy.RANDOM,
        rng=rng,
    )
    seen = set()
    for _ in range(10):
        async with transport.acquire() as proxy:
            assert proxy is not None
            seen.add(str(proxy.url))
    assert len(seen) >= 2


async def test_sticky_per_account():
    transport = ListProxyTransport(
        ["1.1.1.1:8080", "2.2.2.2:8080"],
        strategy=RotationStrategy.STICKY,
    )
    first = None
    for _ in range(5):
        async with transport.acquire(account_id="acc-1") as proxy:
            assert proxy is not None
            if first is None:
                first = str(proxy.url)
            else:
                assert str(proxy.url) == first


async def test_invalid_hook_fires_on_failure():
    transport = ListProxyTransport(["1.1.1.1:8080"], raise_on_ban=False)
    seen: list[tuple[str, str]] = []

    def _hook(proxy, err):
        seen.append((str(proxy.url), type(err).__name__ if err else "None"))

    transport.add_invalid_hook(_hook)
    acquire = transport.acquire()
    async with acquire:
        acquire.mark_invalid(ProxyConnectionError("boom"))
    assert seen and "ProxyConnectionError" in seen[0][1]


def _only_key(transport: ListProxyTransport) -> str:
    return next(iter(transport._health.keys()))


def _last_context(transport: ListProxyTransport):  # noqa: ANN202
    # placeholder to silence unused-helper warning in skipped test path
    return None
