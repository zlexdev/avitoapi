"""Autoteka (vehicle history) domain — VIN/regnum previews + full report DTOs.

Autoteka is a paid surface — the ``POST /autoteka/v1/report`` endpoint
debits balance every call. The SDK does not wrap that with extra safeties
(no rate-limit on top of Avito's own); callers gate it themselves.

Live tests are gated on ``AVITOAPI_LIVE=1`` (W6 ships only unit tests with
canned fixtures).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AutotekaPreview(BaseModel):
    """Free preview returned by ``GET /autoteka/v1/preview``.

    Carries the minimum identifying info plus a single boolean accident flag
    Avito surfaces for free. Full details require a paid :class:`AutotekaFullReport`.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    vin: str | None = Field(
        default=None,
        description="Vehicle VIN; null when the lookup used a registration number.",
    )
    regnum: str | None = Field(
        default=None,
        description="Russian registration plate; null when the lookup used a VIN.",
    )
    brand: str | None = Field(default=None, description="Manufacturer brand.")
    model: str | None = Field(default=None, description="Vehicle model.")
    year: int | None = Field(
        default=None,
        ge=1900,
        le=2100,
        description="Model year.",
    )
    has_accidents: bool = Field(
        default=False,
        description="True when Avito's preview indicates at least one recorded accident.",
    )


class AutotekaFullReport(BaseModel):
    """Paid full report from ``POST /autoteka/v1/report``.

    Avito's full payload is deeply nested, evolving, and partly localised; the
    SDK models ``summary`` + ``sections`` as raw dicts to stay forward-compat.
    Callers who need a fixed shape build their own DTO and validate
    ``report.sections`` against it.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    vin: str = Field(
        ..., description="Vehicle VIN the report covers (always present in full report)."
    )
    summary: dict[str, Any] = Field(
        default_factory=dict,
        description="Headline counters Avito surfaces at the top of the report.",
    )
    sections: dict[str, Any] = Field(
        default_factory=dict,
        description="Detail sections keyed by section name; shape evolves over time.",
    )
