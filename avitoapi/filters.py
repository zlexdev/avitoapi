"""Magic filter ``F`` — attribute/item/comparison capture for event predicates.

::

    from avitoapi import F

    @router.new_message(F.message.type == "text")
    async def on_text(event, ctx): ...

    @router.order_created(F.amount > 1000)
    async def on_big_order(event, ctx): ...

Chain attributes (``F.message.text``), index (``F.payload["chat_id"]``),
compare (``== != > >= < <=``), combine (``& |``), invert (``~``), or use
the named helpers ``F.x.in_({1, 2})`` / ``F.x.contains("foo")`` /
``F.x.func(callable)``.

Each operation returns a new :class:`MagicFilter`; the leaf is a callable
that takes one event and returns ``bool``.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable


class MagicFilter:
    """Chainable predicate builder.

    Internal state is an opaque resolver / predicate pair. Comparison
    operators return a fresh :class:`MagicFilter` whose ``__call__``
    evaluates to ``bool``.
    """

    __slots__ = ("_predicate", "_resolver")

    def __init__(
        self,
        *,
        resolver: Callable[[object], object] = lambda ev: ev,
        predicate: Callable[[object], bool] | None = None,
    ) -> None:
        self._resolver = resolver
        self._predicate = predicate

    def __call__(self, event: object) -> bool:
        if self._predicate is None:
            return bool(self._resolver(event))
        return bool(self._predicate(event))

    def __getattr__(self, name: str) -> MagicFilter:
        if name.startswith("_"):
            raise AttributeError(name)
        prev = self._resolver
        return MagicFilter(resolver=lambda ev: getattr(prev(ev), name, None))

    def __getitem__(self, key: object) -> MagicFilter:
        prev = self._resolver
        return MagicFilter(resolver=lambda ev: _safe_index(prev(ev), key))

    def __eq__(self, other: object) -> MagicFilter:  # type: ignore[override]
        prev = self._resolver
        return MagicFilter(predicate=lambda ev: prev(ev) == other)

    def __ne__(self, other: object) -> MagicFilter:  # type: ignore[override]
        prev = self._resolver
        return MagicFilter(predicate=lambda ev: prev(ev) != other)

    def __gt__(self, other: object) -> MagicFilter:
        prev = self._resolver
        return MagicFilter(predicate=lambda ev: prev(ev) > other)  # type: ignore[operator]  # runtime comparison on opaque objects

    def __ge__(self, other: object) -> MagicFilter:
        prev = self._resolver
        return MagicFilter(predicate=lambda ev: prev(ev) >= other)  # type: ignore[operator]

    def __lt__(self, other: object) -> MagicFilter:
        prev = self._resolver
        return MagicFilter(predicate=lambda ev: prev(ev) < other)  # type: ignore[operator]

    def __le__(self, other: object) -> MagicFilter:
        prev = self._resolver
        return MagicFilter(predicate=lambda ev: prev(ev) <= other)  # type: ignore[operator]

    def __and__(self, other: MagicFilter | Callable[[object], bool]) -> MagicFilter:
        left = self
        return MagicFilter(predicate=lambda ev: left(ev) and other(ev))

    def __or__(self, other: MagicFilter | Callable[[object], bool]) -> MagicFilter:
        left = self
        return MagicFilter(predicate=lambda ev: left(ev) or other(ev))

    def __invert__(self) -> MagicFilter:
        inner = self
        return MagicFilter(predicate=lambda ev: not inner(ev))

    def in_(self, values: Iterable[object]) -> MagicFilter:
        snapshot = tuple(values)
        prev = self._resolver
        return MagicFilter(predicate=lambda ev: prev(ev) in snapshot)

    def contains(self, value: object) -> MagicFilter:
        prev = self._resolver
        return MagicFilter(predicate=lambda ev: _safe_contains(prev(ev), value))

    def func(self, fn: Callable[[object], bool]) -> MagicFilter:
        prev = self._resolver
        return MagicFilter(predicate=lambda ev: bool(fn(prev(ev))))

    __hash__ = None  # type: ignore[assignment]


def _safe_index(obj: object, key: object) -> object:
    try:
        return obj[key]  # type: ignore[index]  # runtime duck-typed indexing
    except (TypeError, KeyError, IndexError):
        return None


def _safe_contains(haystack: object, needle: object) -> bool:
    try:
        return needle in haystack  # type: ignore[operator]  # runtime duck-typed containment
    except TypeError:
        return False


F = MagicFilter()
"""Root magic filter. Use ``F.attr == value`` to build predicates."""


__all__ = ["F", "MagicFilter"]
