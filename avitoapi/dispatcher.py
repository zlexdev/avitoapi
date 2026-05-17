"""Multi-account Dispatcher — aiogram-style: inherits from :class:`Router`.

Sits alongside :class:`Client`, fanning out inbound events. Because
``Dispatcher`` itself is a :class:`Router`, every event observer
(``dispatcher.new_message``, ``dispatcher.order_created``, ...) is
attached directly on the dispatcher — handlers can register without an
intermediate router unless they want plugin-style isolation.

Requires ``evented`` (private dep at ``github.com/zlexdev/evented``); install
via ``pip install 'git+https://${GH_TOKEN}@github.com/zlexdev/evented.git'``.
"""
from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

import evented

from .routers import Router
from .routers._routers import install_observers

if TYPE_CHECKING:
    from .client import Client
    from .storage.base import BaseStorage


class Dispatcher(Router, evented.Dispatcher):
    """SDK-wide aiogram-style Dispatcher.

    Multiple-inherits from :class:`Router` (observer surface) and
    :class:`evented.Dispatcher` (event entry / in-flight task tracking /
    workflow data). Because both ultimately share ``evented.Router``, the
    MRO collapses cleanly to a single Router foundation.
    """

    def __init__(
        self,
        *,
        name: str = "dispatcher",
        **dispatcher_kw: Any,
    ) -> None:
        # Skip Router.__init__ on purpose — evented.Dispatcher handles base
        # initialisation, and we attach observers explicitly afterwards.
        evented.Dispatcher.__init__(self, name=name, **dispatcher_kw)
        install_observers(self)


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
    dispatcher = Dispatcher()
    # Side-channels live as attributes — the current evented Dispatcher signature
    # only accepts cross-cutting bits (concurrency, journals, transport). Storages
    # for FSM / idempotency / DLQ are stitched in by the user at middleware level.
    dispatcher.accounts = {acc.account_id or "_anon": acc for acc in accounts}  # type: ignore[attr-defined]
    if fsm_storage is not None:
        dispatcher.fsm_storage = fsm_storage  # type: ignore[attr-defined]
    if idempotency_storage is not None:
        dispatcher.idempotency_storage = idempotency_storage  # type: ignore[attr-defined]
    elif hasattr(evented, "InMemoryIdempotencyStore"):
        dispatcher.idempotency_storage = evented.InMemoryIdempotencyStore()  # type: ignore[attr-defined]
    if dlq is not None:
        dispatcher.dlq = dlq  # type: ignore[attr-defined]
    elif hasattr(evented, "InMemoryDeadLetterQueue"):
        dispatcher.dlq = evented.InMemoryDeadLetterQueue()  # type: ignore[attr-defined]
    if web is not None:
        dispatcher.web = web  # type: ignore[attr-defined]

    if hasattr(evented, "configure_logging") and hasattr(evented, "LoggingConfig"):
        with contextlib.suppress(Exception):
            evented.configure_logging(evented.LoggingConfig(level=log_level))  # type: ignore[arg-type]

    return dispatcher


__all__ = ["Dispatcher", "make_dispatcher"]
