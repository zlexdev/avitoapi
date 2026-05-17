"""Unit tests for :class:`WebhookIdempotencyMiddleware`."""

from __future__ import annotations

import asyncio
from datetime import timedelta

from avitoapi.storage.memory import MemoryStorage
from avitoapi.web.middlewares.idempotency import WebhookIdempotencyMiddleware


async def test_first_call_not_seen_second_call_seen():
    mw = WebhookIdempotencyMiddleware(MemoryStorage())
    assert await mw.seen("chat-1", "msg-1") is False
    assert await mw.seen("chat-1", "msg-1") is True


async def test_distinct_keys_independent():
    mw = WebhookIdempotencyMiddleware(MemoryStorage())
    assert await mw.seen("chat-1", "msg-1") is False
    assert await mw.seen("chat-1", "msg-2") is False
    assert await mw.seen("chat-2", "msg-1") is False
    # Replays
    assert await mw.seen("chat-1", "msg-1") is True
    assert await mw.seen("chat-2", "msg-1") is True


async def test_ttl_expires():
    mw = WebhookIdempotencyMiddleware(
        MemoryStorage(),
        ttl=timedelta(milliseconds=50),
    )
    assert await mw.seen("c", "m") is False
    assert await mw.seen("c", "m") is True
    await asyncio.sleep(0.08)
    # After TTL the key is reclaimed and the same pair counts as fresh.
    assert await mw.seen("c", "m") is False


async def test_forget_clears_record():
    mw = WebhookIdempotencyMiddleware(MemoryStorage())
    await mw.seen("c", "m")
    await mw.forget("c", "m")
    assert await mw.seen("c", "m") is False
