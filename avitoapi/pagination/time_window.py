"""``TimeWindowPaginator[T]`` — walks ``date_from`` / ``date_to`` + offset endpoints."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING, Generic, TypeVar

from .base import BasePaginator

if TYPE_CHECKING:
    from ..client import Client
    from ..methods._base import BaseMethod

T = TypeVar("T")

_DEFAULT_PAGE_SIZE = 100
_DEFAULT_MAX_OFFSET = 10_000


class TimeWindowPaginator(BasePaginator[T], Generic[T]):
    """Async-iterates date-bounded list endpoints (messenger chats, calls, CPA).

    Walks ``(date_from, date_to, limit, offset)`` shaped methods that return a
    bare ``list[T]``. Stops on:
      * the server returning fewer than ``page_size`` rows, or
      * ``offset`` exceeding ``max_offset`` (Avito caps deep paging).

    The runaway guard from :class:`BasePaginator` fires after ``max_pages`` pages.
    """

    def __init__(
        self,
        client: Client,
        method_factory: Callable[[datetime, datetime, int, int], BaseMethod[object]],
        *,
        date_from: datetime,
        date_to: datetime,
        page_size: int = _DEFAULT_PAGE_SIZE,
        max_offset: int = _DEFAULT_MAX_OFFSET,
        max_pages: int | None = None,
    ) -> None:
        super().__init__(client, max_pages=max_pages)
        if page_size < 1:
            raise ValueError("page_size must be >= 1")
        if max_offset < 0:
            raise ValueError("max_offset must be >= 0")
        if date_to < date_from:
            raise ValueError("date_to must not precede date_from")
        self._factory = method_factory
        self._date_from = date_from
        self._date_to = date_to
        self._page_size = page_size
        self._max_offset = max_offset
        self._offset = 0

    async def _advance(self) -> tuple[list[T], bool]:
        method = self._factory(
            self._date_from,
            self._date_to,
            self._page_size,
            self._offset,
        )
        raw = await self._client(method)
        items: list[T] = self._coerce_to_list(raw)
        has_next = self._has_next(items)
        self._offset += self._page_size
        return items, has_next

    def _has_next(self, items: list[T]) -> bool:
        if not items:
            return False
        if len(items) < self._page_size:
            return False
        return not (self._offset + self._page_size > self._max_offset)
