"""Autoload-domain events — XML feed pipeline lifecycle.

Emitted by the autoload poller around ``GET /autoload/v2/reports``: each
new report id produces :class:`AutoloadReportReady` once parsing finishes,
and :class:`AutoloadFailed` when the report carries fatal errors.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from .messenger import BaseEvent


class AutoloadEvent(BaseEvent, event_name="autoload"):
    """Common ancestor of every autoload-domain event."""

    account_id: str
    report_id: int

    def __init__(self, *, account_id: str, report_id: int, **kwargs: Any) -> None:
        super().__init__()
        self.account_id = account_id
        self.report_id = report_id
        for k, v in kwargs.items():
            setattr(self, k, v)


class AutoloadReportReady(AutoloadEvent, event_name="autoload.report_ready"):
    """A processed feed report is ready for download."""

    section_count: int
    finished_at: datetime

    def __init__(
        self,
        *,
        account_id: str,
        report_id: int,
        section_count: int,
        finished_at: datetime,
    ) -> None:
        super().__init__(account_id=account_id, report_id=report_id)
        self.section_count = section_count
        self.finished_at = finished_at


class AutoloadFailed(AutoloadEvent, event_name="autoload.failed"):
    """The feed run terminated with fatal errors and no items processed."""

    error_count: int
    failed_at: datetime
    message: str | None

    def __init__(
        self,
        *,
        account_id: str,
        report_id: int,
        error_count: int,
        failed_at: datetime,
        message: str | None = None,
    ) -> None:
        super().__init__(account_id=account_id, report_id=report_id)
        self.error_count = error_count
        self.failed_at = failed_at
        self.message = message


__all__ = ["AutoloadEvent", "AutoloadFailed", "AutoloadReportReady"]
