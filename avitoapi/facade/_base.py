"""Typed base for the generated ``*Facade`` mixins — hand-written, never regenerated.

The generated per-domain facades call ``await self.execute(SomeMethod(...))`` (or
``self.paginate(...)`` for paginated endpoints) — i.e. they assume the object they are
mixed into is the :class:`~avitoapi.client.Client`. This base declares that surface
(type-check only) with precise return types so the mixins pass ``mypy --strict`` *and* so
IDE async inspections see ``execute`` as a real coroutine (the overloaded ``__call__``
returned ``MethodPaginator | Coroutine``, which tools flagged as not-awaitable). At runtime
the concrete ``Client`` supplies these.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from ..methods._base import BaseMethod
    from ..pagination import MethodPaginator, PaginatedMethod

TR = TypeVar("TR")


class FacadeBase:
    """Declares the ``Client`` surface the generated facade mixins rely on."""

    if TYPE_CHECKING:

        async def execute(self, method: BaseMethod[TR]) -> TR: ...  # noqa: D102 — Client supplies it

        def paginate(  # noqa: D102 — Client supplies it
            self,
            method: PaginatedMethod[TR],
        ) -> MethodPaginator[Any]: ...

        def __call__(self, method: Any) -> Any: ...  # noqa: D102 — back-compat, provided by Client
