"""Autoload-domain events — XML feed pipeline lifecycle.

Emitted by the autoload poller around ``GET /autoload/v2/reports``: each
new report id produces :class:`AutoloadReportReady` once parsing finishes,
and :class:`AutoloadFailed` when the report carries fatal errors.
"""

from __future__ import annotations

from datetime import datetime

from .messenger import BaseEvent


class AutoloadEvent(BaseEvent, event_name="autoload"):
    """Common ancestor of every autoload-domain event."""

    account_id: str
    report_id: int


class AutoloadReportReady(AutoloadEvent, event_name="autoload.report_ready"):
    """A processed feed report is ready for download."""

    section_count: int
    finished_at: datetime


class AutoloadFailed(AutoloadEvent, event_name="autoload.failed"):
    """The feed run terminated with fatal errors and no items processed."""

    error_count: int
    failed_at: datetime
    message: str | None = None


__all__ = ["AutoloadEvent", "AutoloadFailed", "AutoloadReportReady"]
