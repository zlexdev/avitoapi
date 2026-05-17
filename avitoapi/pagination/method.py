"""Paginated method base classes — declarative ``offset/limit`` and ``page/per_page``.

Concrete endpoint classes inherit from :class:`OffsetMethod` or :class:`PageMethod`
to get pagination fields for free; :class:`Client.__call__` then auto-dispatches
them to a paginator rather than emitting one wire call.
"""
from __future__ import annotations

from typing import Any, ClassVar, Generic, Self, TypeVar

from pydantic import Field

from ..methods._base import BaseMethod

T = TypeVar("T", bound=Any)

_DEFAULT_PAGE_SIZE_OFFSET = 50
_DEFAULT_PAGE_SIZE_NUMBERED = 25
_DEFAULT_MAX_OFFSET = 10_000


class PaginatedMethod(BaseMethod[T], Generic[T]):
    """Marker base for methods that paginate.

    The wire-response type ``T`` is the per-page envelope (``Page[Item]``,
    ``ChatList``, ``RootModel[list[Item]]`` …). Subclasses declare a single
    class-var, ``__items_attr__``, when the items live behind a domain-specific
    attribute (``chats``, ``messages``, ``orders``); the default extractor
    falls back to ``.root``, ``.items``, or a bare list.

    Concrete pagination shape is provided by :class:`OffsetMethod` (``limit`` +
    ``offset``) or :class:`PageMethod` (``page`` + ``per_page``); both
    implement :meth:`_advance` and :meth:`_has_next`.
    """

    __items_attr__: ClassVar[str | None] = None

    def _advance(self) -> Self:
        raise NotImplementedError

    def _page_size(self) -> int:
        raise NotImplementedError

    def _extract_items(self, response: Any) -> list[Any]:
        """Pull the list of items out of one page's response."""

        attr = self.__items_attr__
        if attr is not None:
            value = getattr(response, attr, None)
            if isinstance(value, list):
                return list(value)
            raise TypeError(
                f"{type(self).__name__}: __items_attr__={attr!r} did not yield a list "
                f"on {type(response).__name__}",
            )
        if isinstance(response, list):
            return list(response)
        root = getattr(response, "root", None)
        if isinstance(root, list):
            return list(root)
        items = getattr(response, "items", None)
        if isinstance(items, list):
            return list(items)
        raise TypeError(
            f"{type(self).__name__}: cannot extract items from "
            f"{type(response).__name__}; set __items_attr__ on the method class",
        )

    def _has_next(self, items: list[Any], response: Any) -> bool:  # noqa: ARG002 — override hook
        """Default heuristic: stop when the server returned a partial page."""

        return len(items) >= self._page_size()


class OffsetMethod(PaginatedMethod[T], Generic[T]):
    """``limit`` + ``offset`` paginated method.

    Subclasses inherit the two fields and may override their bounds. The
    ``__max_offset__`` class-var caps deep paging (Avito refuses past 10k on
    several surfaces); the runaway guard on :class:`MethodPaginator` is a
    separate, page-count cap.
    """

    limit: int = Field(default=_DEFAULT_PAGE_SIZE_OFFSET, ge=1)
    offset: int = Field(default=0, ge=0)

    __max_offset__: ClassVar[int] = _DEFAULT_MAX_OFFSET

    def _page_size(self) -> int:
        return self.limit

    def _advance(self) -> Self:
        return self.model_copy(update={"offset": self.offset + self.limit})

    def _has_next(self, items: list[Any], response: Any) -> bool:  # noqa: ARG002 — override hook
        if len(items) < self.limit:
            return False
        return self.offset + self.limit < self.__max_offset__


class PageMethod(PaginatedMethod[T], Generic[T]):
    """``page`` + ``per_page`` paginated method.

    The response is usually a :class:`Page` envelope; ``total`` (when present)
    is honoured to stop early once the cumulative count reaches it.
    """

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=_DEFAULT_PAGE_SIZE_NUMBERED, ge=1)

    def _page_size(self) -> int:
        return self.per_page

    def _advance(self) -> Self:
        return self.model_copy(update={"page": self.page + 1})

    def _has_next(self, items: list[Any], response: Any) -> bool:
        if len(items) < self.per_page:
            return False
        total = getattr(response, "total", None)
        if isinstance(total, int):
            return self.page * self.per_page < total
        return True
