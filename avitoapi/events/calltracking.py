"""Calltracking-domain events — emitted by the calls poller.

Avito's calltracking surface delivers call records on a delay; the poller
diffs successive pages and emits one event per new row.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .messenger import BaseEvent


class CalltrackingEvent(BaseEvent, event_name="calltracking"):
    """Common ancestor of every calltracking event."""

    account_id: str
    call_id: str

    def __init__(self, *, account_id: str, call_id: str, **kwargs: Any) -> None:
        super().__init__()
        self.account_id = account_id
        self.call_id = call_id
        for k, v in kwargs.items():
            setattr(self, k, v)


class CallReceived(CalltrackingEvent, event_name="calltracking.received"):
    """A new call landed against one of the seller's items."""

    item_id: int | None
    received_at: datetime

    def __init__(
        self,
        *,
        account_id: str,
        call_id: str,
        received_at: datetime,
        item_id: int | None = None,
    ) -> None:
        super().__init__(account_id=account_id, call_id=call_id)
        self.received_at = received_at
        self.item_id = item_id


class CallEnded(CalltrackingEvent, event_name="calltracking.ended"):
    """The call finished — duration + answered flag are final."""

    duration_s: int
    answered: bool
    ended_at: datetime

    def __init__(
        self,
        *,
        account_id: str,
        call_id: str,
        duration_s: int,
        answered: bool,
        ended_at: datetime,
    ) -> None:
        super().__init__(account_id=account_id, call_id=call_id)
        self.duration_s = duration_s
        self.answered = answered
        self.ended_at = ended_at


class CallRecordingReady(CalltrackingEvent, event_name="calltracking.recording_ready"):
    """A recording URL is now downloadable for the call."""

    recording_url: str
    ready_at: datetime

    def __init__(
        self,
        *,
        account_id: str,
        call_id: str,
        recording_url: str,
        ready_at: datetime,
    ) -> None:
        super().__init__(account_id=account_id, call_id=call_id)
        self.recording_url = recording_url
        self.ready_at = ready_at


__all__ = [
    "CallEnded",
    "CallReceived",
    "CallRecordingReady",
    "CalltrackingEvent",
]
