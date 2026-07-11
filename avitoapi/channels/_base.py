"""Push-channel contract — a bounded producer→dispatcher pipe with an overflow policy.

Pull ingress (a poller calling ``feed_event`` in a loop) couples the producer to
handler latency: a slow handler stalls the caller. A channel decouples them —
producers ``publish`` into a bounded queue, a drain worker feeds the dispatcher
at its own pace, and the :class:`ChannelOverflow` policy decides what happens
when the queue is full.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..events._base import Event


class ChannelOverflow(StrEnum):
    """What a full channel does with a new event."""

    BLOCK = "block"  # backpressure: await a free slot
    DROP_OLDEST = "drop_oldest"  # evict the oldest queued event, enqueue the new one
    DROP_NEW = "drop_new"  # discard the incoming event
    RAISE = "raise"  # raise ChannelFull to the producer


class ChannelFull(RuntimeError):
    """Raised by :meth:`BaseEventChannel.publish` when overflow is ``RAISE`` and the queue is full."""

    def __init__(self, name: str, maxsize: int) -> None:
        super().__init__(f"channel {name!r} full (maxsize={maxsize})")
        self.name = name
        self.maxsize = maxsize


class ChannelClosed(RuntimeError):
    """Raised when publishing to a closed channel."""

    def __init__(self, name: str) -> None:
        super().__init__(f"channel {name!r} is closed")
        self.name = name


class BaseEventChannel(ABC):
    """A named, bounded event pipe. One producer side, one drain (consumer) side."""

    name: str

    @abstractmethod
    async def publish(self, event: Event) -> bool:
        """Enqueue ``event``. Return ``True`` if accepted, ``False`` if dropped by policy."""

    @abstractmethod
    def stream(self) -> AsyncIterator[Event]:
        """Async-iterate delivered events until the channel is closed."""

    @abstractmethod
    async def close(self) -> None:
        """Stop the channel and unblock the drain. Idempotent."""


__all__ = [
    "BaseEventChannel",
    "ChannelClosed",
    "ChannelFull",
    "ChannelOverflow",
]
