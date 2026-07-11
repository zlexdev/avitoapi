"""``MemoryEventChannel`` — in-process bounded channel over :class:`asyncio.Queue`."""

from __future__ import annotations

import asyncio
import contextlib
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from ._base import BaseEventChannel, ChannelClosed, ChannelFull, ChannelOverflow

if TYPE_CHECKING:
    from ..events._base import Event

_CLOSE = object()  # sentinel pushed on close() to unblock the drain


class MemoryEventChannel(BaseEventChannel):
    """Bounded in-process channel. Single drain consumer (the dispatcher's worker)."""

    def __init__(
        self,
        name: str,
        *,
        maxsize: int = 1000,
        overflow: ChannelOverflow = ChannelOverflow.BLOCK,
    ) -> None:
        self.name = name
        self._maxsize = maxsize
        self._overflow = overflow
        self._queue: asyncio.Queue[object] = asyncio.Queue(maxsize=maxsize)
        self._closed = False

    async def publish(self, event: Event) -> bool:
        if self._closed:
            raise ChannelClosed(self.name)
        if self._overflow is ChannelOverflow.BLOCK:
            await self._queue.put(event)
            return True
        try:
            self._queue.put_nowait(event)
            return True
        except asyncio.QueueFull:
            return self._on_full(event)

    def _on_full(self, event: Event) -> bool:
        if self._overflow is ChannelOverflow.DROP_NEW:
            return False
        if self._overflow is ChannelOverflow.RAISE:
            raise ChannelFull(self.name, self._maxsize)
        # DROP_OLDEST: evict one and retry once.
        with contextlib.suppress(asyncio.QueueEmpty):
            self._queue.get_nowait()
        try:
            self._queue.put_nowait(event)
            return True
        except asyncio.QueueFull:
            return False

    async def stream(self) -> AsyncIterator[Event]:
        while True:
            if self._closed and self._queue.empty():
                return
            try:
                item = self._queue.get_nowait()
            except asyncio.QueueEmpty:
                item = await self._queue.get()  # woken by a publish or the close sentinel
            if item is _CLOSE:
                return
            yield item  # type: ignore[misc]  # non-sentinel items are always Event

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        # Non-blocking: never wait on a full bounded queue. If there's no room the
        # stream drains remaining items and stops on the `_closed`+empty check.
        with contextlib.suppress(asyncio.QueueFull):
            self._queue.put_nowait(_CLOSE)

    def qsize(self) -> int:
        return self._queue.qsize()


__all__ = ["MemoryEventChannel"]
