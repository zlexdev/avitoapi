"""Cross-cutting NewType / Enum / lightweight view types used by every layer."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import NewType

HostKey = NewType("HostKey", str)
"""Logical host identifier (e.g. ``HostKey("www")``). Resolved to a base URL by ClientConfig."""

BreakerKey = NewType("BreakerKey", str)
"""Circuit-breaker scope key. Built from ``(host, path_template[, account_id])``."""


class HealthState(StrEnum):
    """Aggregate state surfaced by ``Client.healthcheck()``."""

    OK = "ok"
    DEGRADED = "degraded"
    DOWN = "down"


@dataclass(slots=True, frozen=True)
class HealthStatus:
    """Snapshot of all health-relevant subsystems."""

    state: HealthState
    storage: bool
    sessions: dict[str, bool] = field(default_factory=dict)
    breakers_open: tuple[str, ...] = ()
    detail: str | None = None
