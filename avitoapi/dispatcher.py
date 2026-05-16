"""Multi-account Dispatcher — thin subclass of ``evented.Dispatcher``.

Sits alongside :class:`Client`, fanning out inbound events. Requires
``evented`` (private dep at ``github.com/zlexdev/evented``); install via
``pip install 'git+https://${GH_TOKEN}@github.com/zlexdev/evented.git'``.
"""
from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

import evented

if TYPE_CHECKING:
    from .client import Client
    from .storage.base import BaseStorage


class Dispatcher(evented.Dispatcher):
    """SDK-wide Dispatcher subclass — placeholder for future hooks."""


def make_dispatcher(
    *,
    accounts: list[Client],
    fsm_storage: BaseStorage[Any, str] | None = None,
    idempotency_storage: BaseStorage[Any, str] | None = None,
    dlq: Any | None = None,
    web: Any | None = None,
    log_level: str = "INFO",
) -> Dispatcher:
    """Build a Dispatcher attached to the given :class:`Client` instances.

    Defaults match what ``evented`` ships in-process: in-memory FSM,
    in-memory idempotency store, in-memory DLQ. Pass real backends for
    multi-process deploys.

    Raises :class:`ImportError` at import time if ``evented`` is missing.
    """
    kwargs: dict[str, Any] = {}
    if fsm_storage is not None:
        kwargs["fsm_storage"] = fsm_storage
    if idempotency_storage is not None:
        kwargs["idempotency_storage"] = idempotency_storage
    elif hasattr(evented, "InMemoryIdempotencyStore"):
        kwargs["idempotency_storage"] = evented.InMemoryIdempotencyStore()
    if dlq is not None:
        kwargs["dlq"] = dlq
    elif hasattr(evented, "InMemoryDeadLetterQueue"):
        kwargs["dlq"] = evented.InMemoryDeadLetterQueue()
    if web is not None:
        kwargs["web"] = web

    dispatcher = Dispatcher(**kwargs)
    dispatcher.accounts = {acc.account_id or "_anon": acc for acc in accounts}  # type: ignore[attr-defined]

    if hasattr(evented, "configure_logging"):
        with contextlib.suppress(Exception):
            evented.configure_logging(level=log_level)

    return dispatcher


__all__ = ["Dispatcher", "make_dispatcher"]
