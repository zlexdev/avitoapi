"""Avitoapi-specific adapters for :mod:`stagecraft`.

Three Protocol implementations that wire the generic stagecraft engine
to avitoapi's :class:`~avitoapi.routers.context.EventContext` shape:

* :class:`QueueMetadataCheckpointStore` — persists checkpoints inside
  ``ctx.queue.metadata`` and flushes them via
  :meth:`CtxQueue.persist_metadata`.
* :class:`AvitoapiStateProvider` — bridges ``ctx.outputs`` +
  ``ctx.pipeline`` (the existing :class:`CtxPipeline`) onto
  :class:`stagecraft.StageRunState`.
* :class:`MiddlewareChainAdapter` — wraps avitoapi's
  :class:`MiddlewareChain` for stagecraft's
  :class:`stagecraft.StageMiddleware` Protocol.

Plus a module-level :func:`completion_hook` that ack's the queue row
via :meth:`EventContext.atomic_completed`.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from stagecraft import StageRunState

    from ..routers.context import CtxPipeline, EventContext
    from ..routers.middleware import MiddlewareChain


class QueueMetadataCheckpointStore:
    """Store stagecraft checkpoints inside the avitoapi queue row.

    Bound to a single :class:`EventContext` — instantiated per
    :meth:`PipelineRunner.run` call so reads/writes hit the right row.
    """

    __slots__ = ("_ctx",)

    def __init__(self, ctx: EventContext) -> None:
        self._ctx = ctx

    async def load(self, key: str) -> dict[str, Any] | None:  # typed-Any: stagecraft CheckpointStore Protocol boundary
        raw = self._ctx.queue.metadata.get(key)
        if isinstance(raw, dict):
            return raw
        return None

    async def save(self, key: str, data: dict[str, Any]) -> None:  # typed-Any: stagecraft CheckpointStore Protocol boundary
        self._ctx.queue.metadata[key] = data
        await self._ctx.queue.persist_metadata()


class _CtxPipelineStateView:
    """Adapter exposing :class:`CtxPipeline` + ``ctx.outputs`` via the
    :class:`stagecraft.StageRunState` Protocol.

    Reads + writes reach through to the live :class:`EventContext` —
    handlers that call ``ctx.pipeline.skip(...)`` from outside the
    pipeline (e.g. an upstream observer) are observed by the runner.
    """

    __slots__ = ("_ctx", "_pipeline_ns")

    def __init__(self, ctx: EventContext) -> None:
        self._ctx = ctx
        self._pipeline_ns: CtxPipeline = ctx.pipeline

    @property
    def outputs(self) -> dict[str, Any]:  # typed-Any: stagecraft StageRunState Protocol boundary
        return self._ctx.outputs

    @property
    def current_pipeline(self) -> str:
        return self._pipeline_ns.current_pipeline

    @current_pipeline.setter
    def current_pipeline(self, value: str) -> None:
        self._pipeline_ns.current_pipeline = value

    @property
    def current_stage(self) -> str:
        return self._pipeline_ns.current_stage

    @current_stage.setter
    def current_stage(self, value: str) -> None:
        self._pipeline_ns.current_stage = value

    @property
    def skip_remaining(self) -> bool:
        return self._pipeline_ns._skip_remaining

    def is_skipped(self, stage_name: str) -> bool:
        return self._pipeline_ns.is_skipped(stage_name)

    def clear_skip(self) -> None:
        self._pipeline_ns.clear_skip()


class AvitoapiStateProvider:
    """:class:`stagecraft.StageStateProvider` for avitoapi
    :class:`EventContext`.

    Stateless — builds a fresh view per :meth:`get_state` call. The
    view's reads / writes hit the real ctx, so handlers see consistent
    state across stages.
    """

    def get_state(self, ctx: Any) -> StageRunState:
        return _CtxPipelineStateView(ctx)  # type: ignore[return-value]  # structural subtype: all StageRunState members present


class MiddlewareChainAdapter:
    """:class:`stagecraft.StageMiddleware` over avitoapi's
    :class:`MiddlewareChain`.

    Forwards :meth:`wrap` so stagecraft sees one ``wrap(terminal)``
    method regardless of the underlying chain shape.
    """

    __slots__ = ("_chain",)

    def __init__(self, chain: MiddlewareChain[Any, Any]) -> None:
        self._chain = chain

    def wrap(
        self,
        terminal: Callable[[Any, Any], Awaitable[Any]],
    ) -> Callable[[Any, Any], Awaitable[Any]]:
        return self._chain.wrap(terminal)


async def completion_hook(ctx: EventContext) -> None:
    """Ack the queue row when the pipeline finishes successfully.

    Idempotent — :meth:`CtxQueue.atomic_completed` is a no-op if the
    row was already acked by an upstream handler.
    """

    if not ctx.queue.is_acked:
        await ctx.atomic_completed()


__all__ = [
    "AvitoapiStateProvider",
    "MiddlewareChainAdapter",
    "QueueMetadataCheckpointStore",
    "completion_hook",
]
