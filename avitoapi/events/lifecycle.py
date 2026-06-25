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

    def __init__(self, *, occurred_at: datetime, **kwargs: object) -> None:
        super().__init__()
        self.occurred_at = occurred_at
        for k, v in kwargs.items():
            setattr(self, k, v)


class Startup(LifecycleEvent, event_name="lifecycle.startup"):
    """The Dispatcher finished wiring accounts and is ready to accept events."""

    account_count: int

    def __init__(self, *, occurred_at: datetime, account_count: int) -> None:
        super().__init__(occurred_at=occurred_at)
        self.account_count = account_count


class Shutdown(LifecycleEvent, event_name="lifecycle.shutdown"):
    """Graceful shutdown started — handlers should finalise side effects."""

    reason: str | None

    def __init__(self, *, occurred_at: datetime, reason: str | None = None) -> None:
        super().__init__(occurred_at=occurred_at)
        self.reason = reason


class TokenRefreshed(LifecycleEvent, event_name="lifecycle.token_refreshed"):
    """An OAuth token was refreshed for one of the bound accounts."""

    account_id: str
    expires_at: datetime

    def __init__(
        self,
        *,
        account_id: str,
        occurred_at: datetime,
        expires_at: datetime,
    ) -> None:
        super().__init__(occurred_at=occurred_at)
        self.account_id = account_id
        self.expires_at = expires_at


class AuthFailed(LifecycleEvent, event_name="lifecycle.auth_failed"):
    """OAuth refresh failed — the account is now in a degraded state."""

    account_id: str
    reason: str

    def __init__(
        self,
        *,
        account_id: str,
        occurred_at: datetime,
        reason: str,
    ) -> None:
        super().__init__(occurred_at=occurred_at)
        self.account_id = account_id
        self.reason = reason


class WebhookError(LifecycleEvent, event_name="lifecycle.webhook_error"):
    """An inbound webhook failed to parse / verify (bad signature, malformed body)."""

    reason: str
    body_preview: str | None

    def __init__(
        self,
        *,
        occurred_at: datetime,
        reason: str,
        body_preview: str | None = None,
    ) -> None:
        super().__init__(occurred_at=occurred_at)
        self.reason = reason
        self.body_preview = body_preview


class PollError(LifecycleEvent, event_name="lifecycle.poll_error"):
    """A poller (orders / items / reviews / ...) crashed mid-iteration."""

    account_id: str
    poller: str
    reason: str

    def __init__(
        self,
        *,
        account_id: str,
        occurred_at: datetime,
        poller: str,
        reason: str,
    ) -> None:
        super().__init__(occurred_at=occurred_at)
        self.account_id = account_id
        self.poller = poller
        self.reason = reason


__all__ = [
    "AuthFailed",
    "LifecycleEvent",
    "PollError",
    "Shutdown",
    "Startup",
    "TokenRefreshed",
    "WebhookError",
]
