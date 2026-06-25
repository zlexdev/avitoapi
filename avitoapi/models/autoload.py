"""Autoload domain — feed-driven listing import reports + profile / upload DTOs.

Autoload is Avito's bulk-listing surface: sellers point Avito at an XML / CSV
feed; Avito polls it on a schedule, produces per-run :class:`AutoloadReport`
documents, and exposes per-item upload status via :class:`AutoloadItemReport`.

The DTOs are read-only with one mutable exception (:class:`AutoloadProfile`,
written by ``UpdateAutoloadProfile``). All models accept extra fields
(``ConfigDict(extra="allow")``) so callers can read forward-compat keys that
Avito ships before this file is bumped.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from ._base import AvitoObject


class AutoloadItemStatus(StrEnum):
    """Per-item upload outcome surfaced inside an Autoload report.

    ``unknown`` is the forward-compat slot for statuses Avito ships after this
    file's last update; the validator never rejects an out-of-band string —
    it lands here via ``extra="allow"`` on the carrying model.
    """

    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class AutoloadItemReport(BaseModel):
    """One row of an Autoload report — outcome for a single feed item."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    ad_id: int = Field(..., description="Avito numeric ad id this row reports on.")
    status: AutoloadItemStatus = Field(
        default=AutoloadItemStatus.UNKNOWN,
        description="Per-item upload outcome.",
    )
    messages: list[str] = Field(
        default_factory=list,
        description="Human-readable per-item diagnostics (validation errors, warnings).",
    )


class AutoloadReport(AvitoObject):
    """One autoload run report.

    No bound methods — Avito has no per-report mutating endpoints. The model
    inherits :class:`AvitoObject` so the session funnel can recursively bind
    nested ``AvitoObject`` instances in mixed-list responses without special
    casing.
    """


    id: str = Field(..., description="Stable report identifier.")
    report_date: datetime = Field(..., description="When the report was generated (UTC).")
    total: int = Field(default=0, ge=0, description="Total items processed in the run.")
    success: int = Field(default=0, ge=0, description="Items uploaded successfully.")
    errors: int = Field(default=0, ge=0, description="Items rejected with an error status.")
    items: list[AutoloadItemReport] = Field(
        default_factory=list,
        description="Per-item rows; empty on the summary list endpoint, populated on detail.",
    )


class AutoloadCategoryFields(BaseModel):
    """Field schema for one Avito category, returned by the v2 fields endpoint.

    Used by clients that programmatically validate their feed before pushing
    it to Avito.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    category_id: int = Field(..., description="Avito numeric category id.")
    required: list[str] = Field(
        default_factory=list,
        description="Field names the category requires for a valid upload.",
    )
    optional: list[str] = Field(
        default_factory=list,
        description="Field names the category accepts but does not require.",
    )


class AutoloadProfile(BaseModel):
    """Autoload schedule + feed-URL profile (one per account).

    Returned by ``GET /autoload/v1/profile`` and persisted via
    ``PUT /autoload/v1/profile`` (idempotent mutation; the SDK auto-injects an
    ``Idempotency-Key`` header).
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    feed_url: HttpUrl | None = Field(
        default=None,
        description="Public URL Avito will poll for the feed; absent on first read.",
    )
    schedule: str | None = Field(
        default=None,
        description="Cron-like schedule string Avito uses to poll the feed.",
    )
    format: str = Field(
        default="xml",
        description="Feed format (``xml`` / ``csv``); Avito accepts strings, not an enum.",
    )


class AutoloadUploadResult(BaseModel):
    """Result envelope for ``POST /autoload/v1/upload`` — feed file ingestion.

    Avito accepts the raw feed file bytes and returns a small acknowledgement
    body. Detailed processing outcomes land in the subsequent report (see
    :class:`AutoloadReport`).
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    accepted: bool = Field(
        default=False,
        description="True when Avito accepted the file for processing.",
    )
    message: str | None = Field(
        default=None,
        description="Optional human-readable acknowledgement / error from Avito.",
    )


class AutoloadIdConversion(BaseModel):
    """Wire envelope for ``GET /autoload/v1/convert?ad_id=`` — id mapping result.

    Avito returns a ``{"<source_id>": <target_id>}`` mapping at the top level
    (no envelope key); the ``mode="before"`` validator rewraps it into the
    :attr:`mapping` field so callers always go through a typed accessor.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    mapping: dict[str, int] = Field(
        default_factory=dict,
        description="Source-id-to-target-id map; usually a single entry per request.",
    )

    @model_validator(mode="before")
    @classmethod
    def _wrap_top_level_mapping(cls, value: object) -> object:
        if isinstance(value, dict) and "mapping" not in value:
            return {"mapping": {str(k): int(v) for k, v in value.items()}}
        return value
