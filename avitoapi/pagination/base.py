"""``BasePaginator`` — shared async-iterator scaffolding with runaway guard."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from ..exceptions import RunawayPagination

if TYPE_CHECKING:
    from ..client import Client

T = TypeVar("T")


class BasePaginator(ABC, Generic[T]):
    """Abstract async-iterable paginator.

    Subclasses implement :meth:`_advance` returning ``(items, has_next)``. The base
    class owns the loop, the page counter, and the runaway guard (``max_pages``,
    default from ``ClientConfig.pagination_max_pages``).
    """

    def __init__(
        self,
        client: Client,
        *,
        max_pages: int | None = None,
    ) -> None:
        self._client = client
        configured = getattr(client.config, "pagination_max_pages", 1000)
        self._max_pages = int(max_pages if max_pages is not None else configured)
        self._pages_fetched = 0
        self._exhausted = False

    @property
    def pages_fetched(self) -> int:
        return self._pages_fetched

    @property
    def exhausted(self) -> bool:
        return self._exhausted

    @abstractmethod
    async def _advance(self) -> tuple[list[T], bool]:
        """Fetch the next page. Returns ``(items, has_next)``.

        Implementations are responsible for mutating any internal cursor state
        (page index, offset, etc.) so the next call advances further.
        """

    def __aiter__(self) -> AsyncIterator[T]:
        return self._iterate()

    async def _iterate(self) -> AsyncIterator[T]:
        while not self._exhausted:
            if self._pages_fetched >= self._max_pages:
                raise RunawayPagination(
                    f"{type(self).__name__}: fetched {self._pages_fetched} pages "
                    f"(max_pages={self._max_pages})",
                )
            items, has_next = await self._advance()
            self._pages_fetched += 1
            for item in items:
                yield item
            if not has_next:
                self._exhausted = True
                return

    @staticmethod
    def _coerce_to_list(value: Any) -> list[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        root = getattr(value, "root", None)
        if root is not None and isinstance(root, list):
            return root
        items = getattr(value, "items", None)
        if isinstance(items, list):
            return items
        raise TypeError(
            f"paginator: cannot extract a list from {type(value).__name__}; "
            "expected list, Page, or RootModel[list[...]]",
        )
