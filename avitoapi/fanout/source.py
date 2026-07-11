"""``BaseEventSource`` — a long-lived stream of events the hub supervises."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..events._base import Event


class BaseEventSource(ABC):
    """One named producer feeding the :class:`~avitoapi.fanout.SourceHub`.

    :meth:`stream` is a long-lived async iterator (a poller loop, a websocket
    read loop, ...). It may raise — the hub restarts it under a
    :class:`~avitoapi.fanout.SupervisionPolicy`. Returning (StopAsyncIteration)
    means the source is finished and is not restarted.
    """

    name: str

    @abstractmethod
    def stream(self) -> AsyncIterator[Event]:
        """Yield events until exhausted or raising (→ supervised restart)."""


__all__ = ["BaseEventSource"]
