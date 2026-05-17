"""Persistent event queue with at-least-once delivery + lease semantics.

Every event entering the :class:`~avitoapi.dispatcher.Dispatcher` is
appended to a :class:`BaseEventQueue`. Consumers — typically a
:class:`QueueWorker` pool — :meth:`lease <EventQueue.lease>` rows,
process them, and :meth:`ack <EventQueue.ack>` on success. Without an
ack inside the visibility window, the row is re-leased automatically.
After ``max_attempts`` strikes the row moves to a
:class:`BaseDeadLetterQueue`.

The queue is storage-agnostic — it composes a
:class:`avitoapi.storage.BaseStorage`. Bring any backend you like.
"""

from __future__ import annotations

from .base import (
    BaseDeadLetterQueue,
    BaseEventQueue,
    DeadLetter,
    MessageLease,
    QueuedEvent,
)
from .dlq import MemoryDeadLetterQueue, StorageDeadLetterQueue
from .queue import EventQueue
from .scheduler import QueueScheduler, enqueue_later, in_seconds
from .serializer import (
    EventRegistrationError,
    EventRegistry,
    EventSerializer,
    JSONSerializer,
    PickleSerializer,
    Upgrader,
)
from .worker import PartitionExtractor, QueueWorker, WorkerHandler

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
