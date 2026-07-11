"""Calltracking-domain events — emitted by the calls poller.

Avito's calltracking surface delivers call records on a delay; the poller
diffs successive pages and emits one event per new row.
"""

from __future__ import annotations

from datetime import datetime

from .messenger import BaseEvent


class CalltrackingEvent(BaseEvent, event_name="calltracking"):
    """Common ancestor of every calltracking event."""

    account_id: str
    call_id: str


class CallReceived(CalltrackingEvent, event_name="calltracking.received"):
    """A new call landed against one of the seller's items."""

    received_at: datetime
    item_id: int | None = None


class CallEnded(CalltrackingEvent, event_name="calltracking.ended"):
    """The call finished — duration + answered flag are final."""

    duration_s: int
    answered: bool
    ended_at: datetime


class CallRecordingReady(CalltrackingEvent, event_name="calltracking.recording_ready"):
    """A recording URL is now downloadable for the call."""

    recording_url: str
    ready_at: datetime


__all__ = [
    "CallEnded",
    "CallReceived",
    "CallRecordingReady",
    "CalltrackingEvent",
]
