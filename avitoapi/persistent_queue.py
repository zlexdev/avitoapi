"""Backward-compatibility shim — moved to :mod:`avitoapi.queue`.

Prefer ``from avitoapi.queue import ...`` going forward. This module
will be removed in a future minor version.
"""

from __future__ import annotations

from .queue import (
    BaseDeadLetterQueue,
    BaseEventQueue,
    DeadLetter,
    EventQueue,
    EventRegistrationError,
    EventRegistry,
    EventSerializer,
    JSONSerializer,
    MemoryDeadLetterQueue,
    MessageLease,
    PartitionExtractor,
    PickleSerializer,
    QueuedEvent,
    QueueScheduler,
    QueueWorker,
    StorageDeadLetterQueue,
    Upgrader,
    WorkerHandler,
    enqueue_later,
    in_seconds,
)

__all__ = [
    "BaseDeadLetterQueue",
    "BaseEventQueue",
    "DeadLetter",
    "EventQueue",
    "EventRegistrationError",
    "EventRegistry",
    "EventSerializer",
    "JSONSerializer",
    "MemoryDeadLetterQueue",
    "MessageLease",
    "PartitionExtractor",
    "PickleSerializer",
    "QueueScheduler",
    "QueueWorker",
    "QueuedEvent",
    "StorageDeadLetterQueue",
    "Upgrader",
    "WorkerHandler",
    "enqueue_later",
    "in_seconds",
]
