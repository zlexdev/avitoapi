"""``MethodPaginator`` — runs a :class:`PaginatedMethod` until exhausted.

The paginator is *both* awaitable and async-iterable:

* ``await client(method)`` — returns the first page's raw envelope (the same
  result you'd get from awaiting a plain :class:`BaseMethod`).
* ``async for item in client(method):`` — walks every page, yields per-item.

The runaway guard caps the page-count (``ClientConfig.pagination_max_pages``,
overridable per-paginator).
"""
from __future__ import annotations

from collections.abc import AsyncIterator, Generator
from typing import TYPE_CHECKING, Any, Generic, Self, TypeVar

from ..exceptions import RunawayPagination

if TYPE_CHECKING:
    from ..client import Client
    from .method import PaginatedMethod

T = TypeVar("T", bound=Any)

_DEFAULT_MAX_PAGES = 1000


class MethodPaginator(Generic[T]):
    """Async-iterates a :class:`PaginatedMethod`, one page at a time.

    Construct via ``client(method)`` rather than directly; the dispatch lives
    in :meth:`Client.__call__`.
    """

    def __init__(
        self,
        client: Client,
        method: PaginatedMethod[Any],
        *,
        max_pages: int | None = None,
    ) -> None:
        self._client = client
        self._method = method
        configured = getattr(client.config, "pagination_max_pages", _DEFAULT_MAX_PAGES)
        self._max_pages = int(max_pages if max_pages is not None else configured)
        self._pages_fetched = 0

    @property
    def pages_fetched(self) -> int:
        return self._pages_fetched

    @property
    def max_pages(self) -> int:
        return self._max_pages

    def with_max_pages(self, max_pages: int) -> Self:
        """Return a fresh paginator with an adjusted runaway cap."""

        return type(self)(self._client, self._method, max_pages=max_pages)

    def __await__(self) -> Generator[Any, None, Any]:
        return self._method.as_(self._client).emit(self._client).__await__()

    def __aiter__(self) -> AsyncIterator[T]:
        return self._iterate()

    async def _iterate(self) -> AsyncIterator[T]:
        method: PaginatedMethod[Any] = self._method
        while True:
            if self._pages_fetched >= self._max_pages:
                raise RunawayPagination(
                    f"{type(method).__name__}: fetched {self._pages_fetched} pages "
                    f"(max_pages={self._max_pages})",
                )
            response = await method.as_(self._client).emit(self._client)
            self._pages_fetched += 1
            items = method._extract_items(response)
            for item in items:
                yield item
            if not method._has_next(items, response):
                return
            method = method._advance()

    async def all(self) -> list[T]:
        """Collect every page into one list. ``RunawayPagination`` if uncapped."""

        return [item async for item in self]

    async def first(self) -> T | None:
        """Return the first item across pages, or ``None`` if empty."""

        async for item in self:
            return item
        return None
