"""Aiogram-style single ``Router`` — every event as a named observer attribute."""
from __future__ import annotations

from ._routers import EventObserver, Router
from .context import CtxPipeline, CtxQueue, EventContext, HandlerType
from .middleware import BaseMiddleware, MiddlewareChain, NextHandler
from .observer import HandlerManager, HandlerSpec

__all__ = [
    "BaseMiddleware",
    "CtxPipeline",
    "CtxQueue",
    "EventContext",
    "EventObserver",
    "HandlerManager",
    "HandlerSpec",
    "HandlerType",
    "MiddlewareChain",
    "NextHandler",
    "Router",
]
