"""Unit tests for the in-package CircuitBreaker + BreakerRegistry."""
from __future__ import annotations

import asyncio

import pytest
from avitoapi.breaker import BreakerRegistry, BreakerState, CircuitBreaker
from avitoapi.config import ClientConfig


def _cfg(**overrides) -> ClientConfig:
    base = dict(
        client_id="x",
        client_secret="y",
        max_retries=0,
        backoff_initial_s=0.001,
        backoff_max_s=0.01,
    )
    base.update(overrides)
    return ClientConfig(**base)


async def test_breaker_opens_after_threshold():
    b = CircuitBreaker(fail_threshold=3, open_seconds=10.0)
    assert b.state is BreakerState.CLOSED
    assert not b.is_open()
    await b.record_failure()
    await b.record_failure()
    assert not b.is_open()
    await b.record_failure()
    assert b.is_open()
    assert b.state is BreakerState.OPEN


async def test_breaker_half_opens_after_timeout():
    b = CircuitBreaker(fail_threshold=2, open_seconds=0.05)
    await b.record_failure()
    await b.record_failure()
    assert b.is_open()
    await asyncio.sleep(0.08)
    # is_open() transitions OPEN -> HALF_OPEN on time check
    assert not b.is_open()
    assert b.state is BreakerState.HALF_OPEN


async def test_breaker_reset_on_success():
    b = CircuitBreaker(fail_threshold=2, open_seconds=0.05)
    await b.record_failure()
    await b.record_failure()
    assert b.is_open()
    await asyncio.sleep(0.08)
    assert not b.is_open()  # half-open
    await b.record_success()
    assert b.state is BreakerState.CLOSED
    assert not b.is_open()


async def test_breaker_half_open_failure_reopens():
    b = CircuitBreaker(fail_threshold=2, open_seconds=0.05)
    await b.record_failure()
    await b.record_failure()
    await asyncio.sleep(0.08)
    assert not b.is_open()  # half-open
    await b.record_failure()
    assert b.is_open()


async def test_breaker_reset_method():
    b = CircuitBreaker(fail_threshold=2, open_seconds=10.0)
    await b.record_failure()
    await b.record_failure()
    assert b.is_open()
    await b.reset()
    assert not b.is_open()
    assert b.state is BreakerState.CLOSED


async def test_registry_caches_by_key():
    reg = BreakerRegistry(_cfg(breaker_fail_threshold=2))
    a = await reg.for_key("api.avito.ru", "/messenger/v1/send")
    b = await reg.for_key("api.avito.ru", "/messenger/v1/send")
    c = await reg.for_key("api.avito.ru", "/items/v3/list")
    assert a is b
    assert a is not c
    assert len(reg) == 2


async def test_registry_per_account_keying():
    reg = BreakerRegistry(_cfg(breaker_per_account=True))
    a = await reg.for_key("api.avito.ru", "/x", "acc-1")
    b = await reg.for_key("api.avito.ru", "/x", "acc-2")
    c = await reg.for_key("api.avito.ru", "/x", "acc-1")
    assert a is c
    assert a is not b
    assert len(reg) == 2


@pytest.mark.parametrize("threshold", [1, 5, 10])
async def test_threshold_parametrized(threshold: int):
    b = CircuitBreaker(fail_threshold=threshold, open_seconds=10.0)
    for _ in range(threshold - 1):
        await b.record_failure()
    assert not b.is_open()
    await b.record_failure()
    assert b.is_open()
