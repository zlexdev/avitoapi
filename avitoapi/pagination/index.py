"""``IndexPaginator[T]`` — walks ``page`` + ``per_page`` shaped endpoints."""
from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Generic, TypeVar

from ..models.common import Page
from .base import BasePaginator

if TYPE_CHECKING:
    from ..client import Client
    from ..methods._base import BaseMethod

T = TypeVar("T")

_DEFAULT_PAGE_SIZE = 25


class IndexPaginator(BasePaginator[T], Generic[T]):
    """Async-iterates ``page=1..N`` against a method factory that returns ``Page[T]``.

    Stops when either:
      * the server returns fewer than ``page_size`` items (last page heuristic), or
      * the cumulative count reaches ``page.total`` when surfaced by Avito.

    The runaway guard from :class:`BasePaginator` fires after ``max_pages`` pages
    regardless of server behaviour.
    """

    def __init__(
        self,
        client: Client,
        method_factory: Callable[[int, int], BaseMethod[Page[T]]],
        *,
        page_size: int = _DEFAULT_PAGE_SIZE,
        start_page: int = 1,
        max_pages: int | None = None,
    ) -> None:
        super().__init__(client, max_pages=max_pages)
        if page_size < 1:
            raise ValueError("page_size must be >= 1")
        if start_page < 1:
            raise ValueError("start_page must be >= 1 (Avito pages start at 1)")
        self._factory = method_factory
        self._page_size = page_size
        self._page = start_page
        self._total: int | None = None
        self._yielded = 0

    async def _advance(self) -> tuple[list[T], bool]:
        method = self._factory(self._page, self._page_size)
        response = await self._client(method)
        raw_items, total = _unwrap_response(response)
        items: list[T] = list(raw_items)  # type: ignore[assignment]
        if total is not None:
            self._total = total
        self._yielded += len(items)
        has_next = self._has_next(items)
        self._page += 1
        return items, has_next

    def _has_next(self, items: list[T]) -> bool:
        if not items:
            return False
        if len(items) < self._page_size:
            return False
        return not (self._total is not None and self._yielded >= self._total)


def _unwrap_response(response: object) -> tuple[list[object], int | None]:
    """Normalise an API response into ``(items, total)``.

    Accepted shapes:
      * ``Page[T]`` — ``items: list[T]`` + ``total: int | None``.
      * ``RootModel[list[T]]`` — ``.root`` is the list.
      * Plain ``list[T]``.
    """
    if isinstance(response, Page):
        return list(response.items), response.total
    root = getattr(response, "root", None)
    if isinstance(root, list):
        return list(root), None
    if isinstance(response, list):
        return list(response), None
    if hasattr(response, "__iter__"):
        return list(response), None  # type: ignore[arg-type]
    raise TypeError(
        f"IndexPaginator cannot iterate response of type {type(response).__name__}",
    )
