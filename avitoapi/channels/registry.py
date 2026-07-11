"""``ChannelRegistry`` — owns push channels and drains each into a sink coroutine."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from ..logging import get_logger

if TYPE_CHECKING:
    from ..events._base import Event
    from ._base import BaseEventChannel

log = get_logger(__name__)

EventSink = Callable[["Event"], Awaitable[Any]]


class ChannelRegistry:
    """Registry of named :class:`BaseEventChannel` with one drain task each.

    ``sink`` is the coroutine every drained event is handed to — the dispatcher
    passes its own ``feed_event``. :meth:`start` is idempotent per channel.
    """

    def __init__(self, sink: EventSink) -> None:
        self._sink = sink
        self._channels: dict[str, BaseEventChannel] = {}
        self._drains: dict[str, asyncio.Task[None]] = {}

    def register(self, channel: BaseEventChannel) -> BaseEventChannel:
        if channel.name in self._channels:
            raise ValueError(f"channel {channel.name!r} already registered")
        self._channels[channel.name] = channel
        return channel

    def get(self, name: str) -> BaseEventChannel | None:
        return self._channels.get(name)

    async def publish(self, name: str, event: Event) -> bool:
        channel = self._channels.get(name)
        if channel is None:
            raise KeyError(f"no channel named {name!r}")
        return await channel.publish(event)

    def start(self) -> None:
        """Spawn a drain task per channel that isn't already draining. Idempotent."""

        for name, channel in self._channels.items():
            task = self._drains.get(name)
            if task is None or task.done():
                self._drains[name] = asyncio.create_task(self._drain(channel))

    async def _drain(self, channel: BaseEventChannel) -> None:
        async for event in channel.stream():
            try:
                await self._sink(event)
            except Exception:  # noqa: BLE001 — one bad event must not kill the drain loop
                log.exception("channel.drain_failed", channel=channel.name)

    async def close(self) -> None:
        """Close every channel and await its drain. Idempotent."""

        for channel in self._channels.values():
            await channel.close()
        if self._drains:
            await asyncio.gather(*self._drains.values(), return_exceptions=True)
            self._drains.clear()


__all__ = ["ChannelRegistry", "EventSink"]
