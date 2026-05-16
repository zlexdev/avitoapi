"""Async paginators for index- and time-window-shaped Avito endpoints."""
from __future__ import annotations

from .base import BasePaginator
from .index import IndexPaginator
from .time_window import TimeWindowPaginator

__all__ = ["BasePaginator", "IndexPaginator", "TimeWindowPaginator"]
