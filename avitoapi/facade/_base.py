"""Typed base for the generated ``*Facade`` mixins — hand-written, never regenerated.

The generated per-domain facades call ``self(SomeMethod(...))`` — i.e. they assume the
object they are mixed into is the callable :class:`~avitoapi.client.Client`. This base
declares that surface (type-check only) so the mixins pass ``mypy --strict`` without every
call needing a ``# type: ignore``. At runtime the concrete ``Client`` supplies ``__call__``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any


class FacadeBase:
    """Declares the ``Client`` surface the generated facade mixins rely on."""

    if TYPE_CHECKING:

        def __call__(self, method: Any) -> Any: ...  # noqa: D102 — provided by Client at runtime
