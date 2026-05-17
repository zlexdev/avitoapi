"""Declarative pagination — methods carry pagination fields, ``Client`` auto-dispatches.

Inherit a list endpoint from :class:`OffsetMethod` (``limit`` + ``offset``) or
:class:`PageMethod` (``page`` + ``per_page``). Awaiting through
``await client(method)`` returns the first page's raw envelope;
``async for item in client(method)`` walks every page.
"""
from __future__ import annotations

from .method import OffsetMethod, PageMethod, PaginatedMethod
from .paginator import MethodPaginator

__all__ = [
    "MethodPaginator",
    "OffsetMethod",
    "PageMethod",
    "PaginatedMethod",
]
