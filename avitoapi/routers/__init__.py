"""Per-domain routers — aiogram-style ``EventObserver`` attributes.

All routers live in :mod:`._routers`. This package re-exports them so
callers can write ``from avitoapi.routers import OrdersRouter``.
"""
from __future__ import annotations

from ._routers import (
    AutoloadRouter,
    BalanceRouter,
    CalltrackingRouter,
    DeliveryRouter,
    EventObserver,
    ItemsRouter,
    LifecycleRouter,
    MessengerRouter,
    OrdersRouter,
    ReviewsRouter,
    Router,
)

__all__ = [
    "AutoloadRouter",
    "BalanceRouter",
    "CalltrackingRouter",
    "DeliveryRouter",
    "EventObserver",
    "ItemsRouter",
    "LifecycleRouter",
    "MessengerRouter",
    "OrdersRouter",
    "ReviewsRouter",
    "Router",
]
