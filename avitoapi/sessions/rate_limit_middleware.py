"""Outbound rate-limit middleware — token bucket per ``(account_id, scope)``.

Backed by ``evented.TokenBucket`` when available, otherwise an in-package
token bucket. Two-tier: global rps per account + per-chat rps for messenger
sends. The middleware inspects ``ctx.workflow_data['chat_id']`` to apply
the per-chat bucket.
"""
from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Any

from .middleware import RequestHandler, RequestMiddleware

if TYPE_CHECKING:
    from ._models import PreparedRequest, RawResponse, RequestContext

try:
    import evented as _evented

    _HAS_EVENTED = hasattr(_evented, "TokenBucket")
except ImportError:
    _evented = None  # type: ignore[assignment]
    _HAS_EVENTED = False


class TokenBucket:
    """In-package token bucket — used when ``evented`` is missing.

    ``rps`` is both the refill rate and the burst capacity. Calling
    :meth:`acquire` waits until one token is available, then consumes it.
    """

    def __init__(self, *, rps: float, capacity: float | None = None) -> None:
        self.rps = float(rps)
        self.capacity = float(capacity) if capacity is not None else float(rps)
        self._tokens = self.capacity
        self._last = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, amount: float = 1.0) -> None:
        """Block until ``amount`` tokens are available, then consume them."""
        while True:
            async with self._lock:
                now = time.monotonic()
                elapsed = now - self._last
                self._tokens = min(self.capacity, self._tokens + elapsed * self.rps)
                self._last = now
                if self._tokens >= amount:
                    self._tokens -= amount
                    return
                deficit = amount - self._tokens
                wait = deficit / self.rps
            await asyncio.sleep(wait)


def _make_bucket(rps: float) -> Any:
    if _HAS_EVENTED:
        return _evented.TokenBucket(rps=rps)
    return TokenBucket(rps=rps)


class AvitoRateLimitMiddleware(RequestMiddleware):
    """Two-tier outbound rate limit: global per account + per-chat for messenger.

    Buckets are stored per ``(account_id, scope)``:

    * ``("acc-1", "_global")`` — every request through that account.
    * ``("acc-1", "chat:42")`` — only messenger sends to chat 42.

    The per-chat bucket fires only when ``ctx.workflow_data['chat_id']``
    is set by the bound method (see :class:`PrepareSendMessage` in W3).
    """

    def __init__(
        self,
        *,
        global_rps: float = 5.0,
        per_chat_rps: float = 1.0,
    ) -> None:
        self.global_rps = float(global_rps)
        self.per_chat_rps = float(per_chat_rps)
        self._buckets: dict[tuple[str, str], Any] = {}
        self._lock = asyncio.Lock()

    async def _bucket_for(self, account_id: str, scope: str, rps: float) -> Any:
        key = (account_id, scope)
        async with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None:
                bucket = _make_bucket(rps)
                self._buckets[key] = bucket
            return bucket

    async def __call__(
        self,
        handler: RequestHandler,
        prepared: PreparedRequest,
        ctx: RequestContext,
    ) -> RawResponse:
        account_id = ctx.account_id or "_anon"
        global_bucket = await self._bucket_for(account_id, "_global", self.global_rps)
        await global_bucket.acquire()

        chat_id = ctx.workflow_data.get("chat_id")
        if chat_id is not None:
            scope = f"chat:{chat_id}"
            chat_bucket = await self._bucket_for(account_id, scope, self.per_chat_rps)
            await chat_bucket.acquire()

        return await handler(prepared, ctx)


__all__ = ["AvitoRateLimitMiddleware", "TokenBucket"]
