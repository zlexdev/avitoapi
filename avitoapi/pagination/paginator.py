"""``MethodPaginator`` / ``CursorPaginator`` — drive paginated methods to exhaustion.

Two paginator variants:

* :class:`MethodPaginator` (alias :data:`IndexPaginator`) — offset/page-indexed
  endpoints.  Works with any :class:`~avitoapi.pagination.method.PaginatedMethod`
  subclass (:class:`~avitoapi.pagination.method.OffsetMethod` or
  :class:`~avitoapi.pagination.method.PageMethod`).  Optionally persists the
  current page position in a :class:`~avitoapi.storage.base.BaseStorage` so
  iterations survive process restarts and two independent callers with different
  ``caller_id`` values don't stomp on each other's state.

* :class:`CursorPaginator` — opaque-cursor endpoints.  Accepts a plain
  ``async (cursor: str | None) -> CursorPage[T]`` callable; no method class
  required.  Same optional storage/persistence contract as ``MethodPaginator``.

* :class:`CursorPage` — lightweight envelope returned by one page of a
  cursor-based endpoint.

The runaway guard caps the page-count (``ClientConfig.pagination_max_pages``
on :class:`MethodPaginator`, or ``max_pages`` kwarg).
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable, Generator
from dataclasses import dataclass, field
from typing import (  # typed-Any: PaginatedMethod[Any] = erased-T holder
    TYPE_CHECKING,
    Any,
    Generic,
    Self,
    TypeVar,
)

from ..exceptions import RunawayPagination

if TYPE_CHECKING:
    from ..client import Client
    from ..storage.base import BaseStorage
    from .method import PaginatedMethod

T = TypeVar("T")

_DEFAULT_MAX_PAGES = 1000


def _page_storage_key(paginator_id: str, caller_id: str) -> str:
    return f"paginator:{paginator_id}:{caller_id}"


@dataclass
class CursorPage(Generic[T]):
    """Envelope for one page in a cursor-based paginated endpoint.

    Args:
        items: Items on this page.
        next_cursor: Opaque cursor for the next page; ``None`` signals the last
            page.
    """

    items: list[T] = field(default_factory=list)
    next_cursor: str | None = None


class MethodPaginator(Generic[T]):
    """Async-iterates a :class:`PaginatedMethod`, one page at a time.

    Construct via ``client(method)`` rather than directly; the dispatch lives
    in :meth:`Client.__call__`.

    Optional persistence: pass *storage* + *paginator_id* to checkpoint the
    current page position across process restarts.  Use distinct *caller_id*
    values for logically separate callers operating on the same endpoint so
    their cursors never collide.

    Args:
        client: Bound :class:`~avitoapi.client.Client`.
        method: The paginated method describing the endpoint and pagination
            parameters.
        max_pages: Hard cap on pages fetched (overrides
            ``ClientConfig.pagination_max_pages``).
        storage: Optional :class:`~avitoapi.storage.base.BaseStorage` for
            cross-request cursor persistence.
        paginator_id: Logical name used as the storage key prefix; defaults to
            the method's class name.
        caller_id: Per-caller discriminator appended to the storage key.
    """

    def __init__(
        self,
        client: Client,
        method: PaginatedMethod[Any],
        *,
        max_pages: int | None = None,
        storage: BaseStorage[object, object] | None = None,
        paginator_id: str | None = None,
        caller_id: str = "default",
    ) -> None:
        self._client = client
        self._method = method
        configured = getattr(client.config, "pagination_max_pages", _DEFAULT_MAX_PAGES)
        self._max_pages = int(max_pages if max_pages is not None else configured)
        self._pages_fetched = 0
        self._storage = storage
        self._paginator_id = paginator_id or type(method).__name__
        self._caller_id = caller_id


    def _storage_key(self) -> str:
        return _page_storage_key(self._paginator_id, self._caller_id)

    async def _load_method_state(self) -> PaginatedMethod[Any]:
        """Restore saved pagination position from storage (if any)."""
        if self._storage is None:
            return self._method
        saved = await self._storage.get(self._storage_key())
        if not isinstance(saved, dict):
            return self._method
        return self._method.model_copy(update=saved)

    async def _save_method_state(self, method: PaginatedMethod[Any]) -> None:
        """Checkpoint current pagination position for the next session."""
        if self._storage is None:
            return
        from .method import OffsetMethod, PageMethod  # noqa: PLC0415 — local avoids cycle

        if isinstance(method, OffsetMethod):
            await self._storage.put(self._storage_key(), {"offset": method.offset})
        elif isinstance(method, PageMethod):
            await self._storage.put(self._storage_key(), {"page": method.page})


    @property
    def pages_fetched(self) -> int:
        return self._pages_fetched

    @property
    def max_pages(self) -> int:
        return self._max_pages

    def with_max_pages(self, max_pages: int) -> Self:
        """Return a fresh paginator with an adjusted runaway cap."""
        return type(self)(
            self._client,
            self._method,
            max_pages=max_pages,
            storage=self._storage,
            paginator_id=self._paginator_id,
            caller_id=self._caller_id,
        )

    async def fetch_page(
        self,
        *,
        cursor: str | None = None,  # noqa: ARG002 — cursor is for CursorPaginator symmetry
        page: int | None = None,
    ) -> object:
        """Fetch a specific page without advancing the iterator state.

        Args:
            page: 1-based page number.  For :class:`~avitoapi.pagination.OffsetMethod`
                this maps to ``offset = (page - 1) * limit``; for
                :class:`~avitoapi.pagination.PageMethod` it sets ``page`` directly.
            cursor: Ignored for index-based paginators; present for API symmetry
                with :class:`CursorPaginator`.

        Returns:
            The raw page envelope — same value as ``await client(method)``.
        """
        from .method import OffsetMethod, PageMethod  # noqa: PLC0415

        method = self._method
        if page is not None:
            if isinstance(method, PageMethod):
                method = method.model_copy(update={"page": page})
            elif isinstance(method, OffsetMethod):
                method = method.model_copy(update={"offset": (page - 1) * method.limit})
        return await method.as_(self._client).emit(self._client)

    def __await__(self) -> Generator[Any, None, T]:  # typed-Any: asyncio yield type is opaque
        return self._method.as_(self._client).emit(self._client).__await__()

    def __aiter__(self) -> AsyncIterator[T]:
        return self._iterate()

    async def _iterate(self) -> AsyncIterator[T]:
        method: PaginatedMethod[Any] = await self._load_method_state()
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
            await self._save_method_state(method)

    async def all(self) -> list[T]:
        """Collect every page into one list. ``RunawayPagination`` if uncapped."""
        return [item async for item in self]

    async def first(self) -> T | None:
        """Return the first item across pages, or ``None`` if empty."""
        async for item in self:
            return item
        return None


#: Alias for :class:`MethodPaginator` — explicit name for index/offset paginators.
IndexPaginator = MethodPaginator


class CursorPaginator(Generic[T]):
    """Async-iterates a cursor-based paginated endpoint.

    Unlike :class:`MethodPaginator`, ``CursorPaginator`` accepts a plain async
    callable so it wraps any cursor-advancing API surface without needing a
    :class:`~avitoapi.pagination.method.PaginatedMethod` subclass.

    Args:
        fetch_fn: ``async (cursor: str | None) -> CursorPage[T]`` — called with
            ``None`` on the first page, then with the previous page's
            :attr:`~CursorPage.next_cursor` until that is ``None``.
        storage: Optional backend to persist the last-seen cursor across
            restarts.  Two callers with different ``caller_id`` values maintain
            independent positions under distinct keys.
        paginator_id: Logical name used as the storage key prefix.
        caller_id: Per-caller discriminator appended to the storage key.
        max_pages: Hard cap on pages fetched.
    """

    def __init__(
        self,
        fetch_fn: Callable[[str | None], Awaitable[CursorPage[T]]],
        *,
        storage: BaseStorage[object, object] | None = None,
        paginator_id: str = "cursor",
        caller_id: str = "default",
        max_pages: int | None = None,
    ) -> None:
        self._fetch_fn = fetch_fn
        self._storage = storage
        self._paginator_id = paginator_id
        self._caller_id = caller_id
        self._max_pages = max_pages or _DEFAULT_MAX_PAGES
        self._pages_fetched = 0

    def _storage_key(self) -> str:
        return _page_storage_key(self._paginator_id, self._caller_id)

    async def _load_cursor(self) -> str | None:
        if self._storage is None:
            return None
        saved = await self._storage.get(self._storage_key())
        if isinstance(saved, dict):
            return saved.get("cursor")
        return None

    async def _save_cursor(self, cursor: str | None) -> None:
        if self._storage is None or cursor is None:
            return
        await self._storage.put(self._storage_key(), {"cursor": cursor})

    @property
    def pages_fetched(self) -> int:
        return self._pages_fetched

    async def fetch_page(
        self,
        *,
        cursor: str | None = None,
        page: int | None = None,  # noqa: ARG002 — page is for MethodPaginator symmetry
    ) -> CursorPage[T]:
        """Fetch a specific page by cursor without advancing iterator state.

        Args:
            cursor: Opaque cursor value returned by a previous page's
                :attr:`~CursorPage.next_cursor`.  ``None`` fetches the first
                page.
            page: Ignored for cursor-based paginators; present for API symmetry
                with :class:`MethodPaginator`.

        Returns:
            A :class:`CursorPage` envelope with items and the next cursor.
        """
        return await self._fetch_fn(cursor)

    def __aiter__(self) -> AsyncIterator[T]:
        return self._iterate()

    async def _iterate(self) -> AsyncIterator[T]:
        cursor: str | None = await self._load_cursor()
        while True:
            if self._pages_fetched >= self._max_pages:
                raise RunawayPagination(
                    f"CursorPaginator: fetched {self._pages_fetched} pages "
                    f"(max_pages={self._max_pages})",
                )
            page = await self._fetch_fn(cursor)
            self._pages_fetched += 1
            for item in page.items:
                yield item
            cursor = page.next_cursor
            await self._save_cursor(cursor)
            if cursor is None:
                return

    async def all(self) -> list[T]:
        """Collect every page into one list."""
        return [item async for item in self]

    async def first(self) -> T | None:
        """Return the first item, or ``None`` if empty."""
        async for item in self:
            return item
        return None
