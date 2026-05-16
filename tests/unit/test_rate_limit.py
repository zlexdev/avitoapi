"""Unit tests for :class:`AvitoRateLimitMiddleware`."""
from __future__ import annotations

import asyncio
import time

from avitoapi.sessions._models import PreparedRequest, RawResponse, RequestContext
from avitoapi.sessions.rate_limit_middleware import (
    AvitoRateLimitMiddleware,
    TokenBucket,
)


async def test_token_bucket_acquire_blocks_after_burst():
    bucket = TokenBucket(rps=10.0)  # capacity 10
    # burn the burst
    for _ in range(10):
        await bucket.acquire()
    start = time.monotonic()
    await bucket.acquire()  # must wait ~0.1s
    elapsed = time.monotonic() - start
    assert elapsed >= 0.05, f"acquire returned too fast: {elapsed:.3f}s"


async def _noop_handler(prepared: PreparedRequest, ctx: RequestContext) -> RawResponse:
    return RawResponse(status=200, headers={}, body=b"", elapsed_s=0.0)


async def test_global_rps_limits_throughput():
    mw = AvitoRateLimitMiddleware(global_rps=5.0, per_chat_rps=1000.0)
    prepared = PreparedRequest(host="www", http_method="GET", url="/x")
    ctx = RequestContext(client=None, account_id="acc-1")

    start = time.monotonic()
    # 5 requests fit in the burst, the 6th must wait ~0.2s.
    for _ in range(6):
        await mw(_noop_handler, prepared, ctx)
    elapsed = time.monotonic() - start
    assert elapsed >= 0.1, f"6 requests at 5 rps came back in {elapsed:.3f}s"


async def test_distinct_accounts_independent():
    mw = AvitoRateLimitMiddleware(global_rps=2.0, per_chat_rps=1000.0)
    prepared = PreparedRequest(host="www", http_method="GET", url="/x")

    async def burn(acc_id: str) -> None:
        ctx = RequestContext(client=None, account_id=acc_id)
        for _ in range(2):  # exact burst, no wait
            await mw(_noop_handler, prepared, ctx)

    start = time.monotonic()
    await asyncio.gather(burn("acc-1"), burn("acc-2"), burn("acc-3"))
    elapsed = time.monotonic() - start
    # 3 accounts × 2 requests at 2rps burst — should all fit without waiting.
    assert elapsed < 0.5, f"distinct accounts shared a bucket; elapsed={elapsed:.3f}s"


async def test_per_chat_bucket_fires_when_chat_id_set():
    mw = AvitoRateLimitMiddleware(global_rps=1000.0, per_chat_rps=2.0)
    prepared = PreparedRequest(host="www", http_method="POST", url="/send")
    ctx = RequestContext(client=None, account_id="acc-1")
    ctx.workflow_data["chat_id"] = "chat-42"

    start = time.monotonic()
    for _ in range(3):  # 2 burst + 1 wait at 2 rps
        await mw(_noop_handler, prepared, ctx)
    elapsed = time.monotonic() - start
    assert elapsed >= 0.3, f"per-chat bucket did not throttle; elapsed={elapsed:.3f}s"
