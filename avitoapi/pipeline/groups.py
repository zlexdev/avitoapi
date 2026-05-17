"""``ParallelGroup`` — fan-out sugar for stages that should run concurrently.

A :class:`ParallelGroup` registers in a :class:`~avitoapi.pipeline.pipeline.Pipeline`
as a single named stage whose ``fn`` gathers sub-stages via
:func:`asyncio.gather`. Use when two side effects are independent and
you'd rather not flatten them into top-level stages with explicit
``depends_on`` arrows.

For fork/join with real dependency arrows across the whole pipeline,
prefer ``Stage(..., depends_on=("..."))`` — the runner topologically
sorts and parallelises layers itself.
"""

from __future__ import annotations

import asyncio
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .pipeline import Stage, StageFn

if TYPE_CHECKING:
    from ..events._base import Event
    from ..routers.context import EventContext
    from ..routers.observer import Filter


@dataclass(slots=True)
class ParallelGroup:
    """Group of stage callables run concurrently as one named pipeline stage.

    The group succeeds when every sub-stage succeeds; the first raised
    exception cancels siblings and propagates (so saga compensation
    works at the group level). Per-stage compensation inside a group
    isn't tracked — the group either ran or it didn't.
    """

    name: str
    members: list[Stage] = field(default_factory=list)

    def add(
        self,
        name: str,
        fn: StageFn,
        *,
        timeout: float | None = None,
    ) -> Stage:
        stage = Stage(name=name, fn=fn, timeout=timeout)
        self.members.append(stage)
        return stage

    def as_stage(
        self,
        *,
        output: str | None = None,
        when: Filter | None = None,
        depends_on: Iterable[str] = (),
    ) -> Stage:
        """Materialise the group as a single :class:`Stage` for a pipeline."""

        members = tuple(self.members)

        async def _run_group(event: Event, ctx: EventContext) -> dict[str, Any]:
            results = await asyncio.gather(
                *(_invoke_member(m, event, ctx) for m in members),
                return_exceptions=False,
            )
            return {m.name: r for m, r in zip(members, results, strict=True)}

        return Stage(
            name=self.name,
            fn=_run_group,
            output=output,
            when=when,
            depends_on=tuple(depends_on),
        )


async def _invoke_member(stage: Stage, event: Event, ctx: EventContext) -> Any:
    if stage.timeout is not None:
        return await asyncio.wait_for(stage.fn(event, ctx), timeout=stage.timeout)
    return await stage.fn(event, ctx)


__all__ = ["ParallelGroup"]
