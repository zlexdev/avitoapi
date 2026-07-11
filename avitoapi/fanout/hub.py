"""``SourceHub`` — merge N supervised event sources into one dispatcher.

Each source runs in its own supervised pump task: it drains ``source.stream()``
into a shared bounded :class:`~avitoapi.channels.MemoryEventChannel`. A single
drain task pulls that channel into ``dispatcher.feed_event`` (so dedup +
auto-ack are reused, and the channel gives backpressure). A source that raises
is restarted under the :class:`SupervisionPolicy`; :meth:`health` reports the
live/failed/restart tally.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..channels import ChannelOverflow, MemoryEventChannel
from ..logging import get_logger
from .supervision import SupervisionPolicy

if TYPE_CHECKING:
    from ..dispatcher import Dispatcher
    from .source import BaseEventSource

log = get_logger(__name__)


@dataclass(slots=True)
class _SourceState:
    alive: bool = False
    restarts: int = 0
    last_error: str | None = None


@dataclass(frozen=True, slots=True)
class SourceHealth:
    """Point-in-time health of one supervised source."""

    name: str
    alive: bool
    restarts: int
    last_error: str | None


@dataclass(frozen=True, slots=True)
class HubHealth:
    """Aggregated health across every source in the hub."""

    sources: list[SourceHealth] = field(default_factory=list)

    @property
    def alive(self) -> int:
        return sum(1 for s in self.sources if s.alive)

    @property
    def failed(self) -> int:
        return sum(1 for s in self.sources if not s.alive)

    @property
    def total_restarts(self) -> int:
        return sum(s.restarts for s in self.sources)


class SourceHub:
    """Supervise many :class:`BaseEventSource` into one :class:`Dispatcher`."""

    def __init__(
        self,
        *,
        dispatcher: Dispatcher,
        supervision: SupervisionPolicy | None = None,
        channel_name: str = "fanout",
        channel_maxsize: int = 1000,
        channel_overflow: ChannelOverflow = ChannelOverflow.BLOCK,
    ) -> None:
        self._dispatcher = dispatcher
        self._supervision = supervision or SupervisionPolicy()
        self._channel = MemoryEventChannel(
            channel_name,
            maxsize=channel_maxsize,
            overflow=channel_overflow,
        )
        self._sources: dict[str, BaseEventSource] = {}
        self._states: dict[str, _SourceState] = {}
        self._pumps: dict[str, asyncio.Task[None]] = {}
        self._drain: asyncio.Task[None] | None = None
        self._running = False

    def add_source(self, source: BaseEventSource) -> None:
        if source.name in self._sources:
            raise ValueError(f"source {source.name!r} already added")
        self._sources[source.name] = source
        self._states[source.name] = _SourceState()

    async def start(self) -> None:
        """Start the channel drain and one supervised pump per source. Idempotent."""

        if self._running:
            return
        self._running = True
        self._drain = asyncio.create_task(self._drain_loop())
        for name, source in self._sources.items():
            self._pumps[name] = asyncio.create_task(self._supervise(source))

    async def _drain_loop(self) -> None:
        async for event in self._channel.stream():
            try:
                await self._dispatcher.feed_event(event)
            except Exception:  # noqa: BLE001 — one bad event must not kill the drain
                log.exception("fanout.drain_failed")

    async def _supervise(self, source: BaseEventSource) -> None:
        state = self._states[source.name]
        attempt = 0
        while self._running:
            produced = False
            try:
                state.alive = True
                async for event in source.stream():
                    produced = True
                    await self._channel.publish(event)
                state.alive = False
                return  # stream exhausted cleanly — source is done
            except asyncio.CancelledError:
                state.alive = False
                raise
            except Exception as exc:  # noqa: BLE001 — isolate + restart one source, never kill the hub
                state.alive = False
                state.restarts += 1
                state.last_error = str(exc)
                log.warning(
                    "fanout.source_failed",
                    source=source.name,
                    restarts=state.restarts,
                    error=str(exc),
                )
                if self._supervision.gives_up(state.restarts):
                    log.error("fanout.source_giving_up", source=source.name)
                    return
                attempt = 0 if produced else attempt + 1
                await asyncio.sleep(self._supervision.delay_for(attempt))

    async def stop(self, *, drain: bool = True) -> None:
        """Stop the pumps, then the drain. ``drain=True`` flushes queued events first."""

        self._running = False
        for task in self._pumps.values():
            task.cancel()
        if self._pumps:
            await asyncio.gather(*self._pumps.values(), return_exceptions=True)
            self._pumps.clear()
        if self._drain is not None:
            if drain:
                await self._channel.close()  # sentinel after queued events → drain flushes then exits
                await self._drain
            else:
                self._drain.cancel()
                await asyncio.gather(self._drain, return_exceptions=True)
                await self._channel.close()
            self._drain = None

    def health(self) -> HubHealth:
        return HubHealth(
            sources=[
                SourceHealth(
                    name=name,
                    alive=state.alive,
                    restarts=state.restarts,
                    last_error=state.last_error,
                )
                for name, state in self._states.items()
            ],
        )


__all__ = ["HubHealth", "SourceHealth", "SourceHub"]
