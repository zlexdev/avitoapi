"""Call-tracking domain — call metadata + audio recording DTOs.

Two surfaces:

* :class:`Call` — JSON call metadata (timestamps, duration, status).
* ``GET /calltracking/v2/calls/{call_id}/recording`` — raw ``audio/mpeg`` body.
  The recording does NOT decode into a model; the corresponding method-class
  sets ``__binary_response__ = True`` so :class:`RestProtocol.decode_response`
  short-circuits and returns ``raw.body`` (``bytes``) verbatim.
"""
from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, RootModel


class CallStatus(StrEnum):
    """Call disposition returned by Avito on the calltracking endpoints.

    ``unknown`` absorbs forward-compat values (Avito has added niche statuses
    over time without bumping the surface).
    """

    ANSWERED = "answered"
    MISSED = "missed"
    REJECTED = "rejected"
    UNKNOWN = "unknown"


class Call(BaseModel):
    """One call event from ``/calltracking/v2/calls``.

    Recording is fetched via a separate method-class (``GetCallRecording``)
    that returns the raw ``audio/mpeg`` bytes; this model only carries the
    URL when Avito surfaces it inline.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    id: str = Field(..., description="Stable call identifier (string, not int).")
    item_id: int | None = Field(
        default=None,
        description="Avito item id the call was about; null on owner-direct calls.",
    )
    phone: str | None = Field(
        default=None,
        description="Counterparty phone in international format (may be masked).",
    )
    duration_s: int = Field(
        default=0,
        ge=0,
        description="Call duration in whole seconds; 0 for missed / rejected calls.",
    )
    status: CallStatus = Field(
        default=CallStatus.UNKNOWN,
        description="Call disposition.",
    )
    recording_url: HttpUrl | None = Field(
        default=None,
        description="Pre-signed recording URL when Avito surfaces one inline.",
    )
    created_at: datetime = Field(..., description="Call start timestamp (UTC).")


class CallList(RootModel[list[Call]]):
    """Top-level JSON array envelope for ``GET /calltracking/v2/calls``.

    Avito returns a bare JSON array; :class:`BaseMethod.__returning__` requires
    a Pydantic model, so we wrap in a :class:`RootModel` and expose iteration
    / length so callers can ``for call in calls`` without unwrapping.
    """

    root: list[Call] = Field(default_factory=list)

    def __iter__(self) -> Iterator[Call]:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class CallRecording(BaseModel):
    """Wrapper DTO for the raw recording bytes.

    Reserved for future evolution — today the recording endpoint uses
    ``__binary_response__ = True`` and returns raw ``bytes`` directly (no
    Pydantic model in the loop). The class is kept so callers can refer to
    it in type hints if they later wrap recordings into their own structures.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    call_id: str = Field(..., description="Owning call id.")
    audio: bytes = Field(..., description="Raw audio bytes (typically ``audio/mpeg``).")
