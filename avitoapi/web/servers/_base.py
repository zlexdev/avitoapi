"""Base contracts for HTTP-framework backends.

Every backend (aiohttp, FastAPI, Litestar, Sanic) implements two classes:

* :class:`BaseWebApp` — owns the framework-native app object and mounts
  :class:`~avitoapi.web.server.Webhook` descriptors as routes.
* :class:`BaseWebhookRunner` — boots the app onto a TCP socket and
  shuts it down cleanly. ``start()`` is fire-and-block; ``stop()`` is
  cooperative cancellation-safe.

The dispatcher is referenced only so subclasses can attach app-level
hooks (e.g. startup log lines). Webhook handlers receive the parsed
JSON body, never the dispatcher directly — they close over it.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from ...logging import get_logger

if TYPE_CHECKING:
    from ...dispatcher import Dispatcher
    from ..server import Webhook, WebhookConfig

log = get_logger(__name__)


class BaseWebApp(ABC):
    """Framework-native application wrapper.

    Subclasses lazy-import their HTTP framework in ``__init__`` so
    importing :mod:`avitoapi.web` never forces a transitive dep.
    """

    app: Any

    @abstractmethod
    def register_webhook(self, webhook: Webhook) -> None:
        """Mount ``webhook`` on the underlying app under its path/method."""


class BaseWebhookRunner(ABC):
    """Drive a :class:`BaseWebApp` over a TCP socket.

    Lifecycle: build app from ``config.webhooks`` in ``__init__``,
    :meth:`start` blocks (or returns a long-lived task), :meth:`stop`
    cancels gracefully.
    """

    app: BaseWebApp

    def __init__(self, *, dispatcher: Dispatcher, config: WebhookConfig) -> None:
        self.dispatcher = dispatcher
        self.config = config
        self.app = self._build_app()
        for webhook in config.webhooks:
            self.app.register_webhook(webhook)

    @abstractmethod
    def _build_app(self) -> BaseWebApp:
        """Construct the framework-specific :class:`BaseWebApp`."""

    @abstractmethod
    async def start(self) -> None:
        """Bind the socket and serve. Blocks until cancelled."""

    @abstractmethod
    async def stop(self) -> None:
        """Stop accepting new connections, drain, then return."""


__all__ = ["BaseWebApp", "BaseWebhookRunner"]
