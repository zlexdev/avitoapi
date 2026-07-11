"""SDK lifecycle events — emitted by the Dispatcher / Client itself.

Not tied to Avito's wire surface; these surface internal state changes
handlers usually want: bootstrap, graceful shutdown, OAuth refresh,
auth failures, webhook decode errors, poller errors. Anything a
running multi-account deployment wants in Sentry/Grafana.
"""

from __future__ import annotations

from datetime import datetime

from .messenger import BaseEvent


class LifecycleEvent(BaseEvent, event_name="lifecycle"):
    """Common ancestor of every SDK-internal lifecycle event."""

    occurred_at: datetime


class Startup(LifecycleEvent, event_name="lifecycle.startup"):
    """The Dispatcher finished wiring accounts and is ready to accept events."""

    account_count: int


class Shutdown(LifecycleEvent, event_name="lifecycle.shutdown"):
    """Graceful shutdown started — handlers should finalise side effects."""

    reason: str | None = None


class TokenRefreshed(LifecycleEvent, event_name="lifecycle.token_refreshed"):
    """An OAuth token was refreshed for one of the bound accounts."""

    account_id: str
    expires_at: datetime


class AuthFailed(LifecycleEvent, event_name="lifecycle.auth_failed"):
    """OAuth refresh failed — the account is now in a degraded state."""

    account_id: str
    reason: str


class WebhookError(LifecycleEvent, event_name="lifecycle.webhook_error"):
    """An inbound webhook failed to parse / verify (bad signature, malformed body)."""

    reason: str
    body_preview: str | None = None


class PollError(LifecycleEvent, event_name="lifecycle.poll_error"):
    """A poller (orders / items / reviews / ...) crashed mid-iteration."""

    account_id: str
    poller: str
    reason: str


__all__ = [
    "AuthFailed",
    "LifecycleEvent",
    "PollError",
    "Shutdown",
    "Startup",
    "TokenRefreshed",
    "WebhookError",
]
