"""Cross-cutting NewType / Enum / lightweight view types used by every layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import NewType, TypeAlias

# Recursive JSON value — the precise type of any decoded JSON. Use instead of ``Any``
# for genuinely free-form wire payloads (HTTP bodies, opaque Avito bags).
JSONValue: TypeAlias = (
    "dict[str, JSONValue] | list[JSONValue] | str | int | float | bool | None"
)

# Free-form JSON object passthrough — use only when the upstream schema is genuinely
# opaque (e.g. Avito returns a volatile payload bag). Prefer typed Pydantic models.
JsonObject: TypeAlias = dict[str, "JSONValue"]

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
