"""Autoteka (vehicle history) endpoints — preview by VIN/regnum + paid full report.

Three method-classes:

* :class:`AutotekaPreviewByVin` — free preview keyed by VIN.
* :class:`AutotekaPreviewByRegnum` — free preview keyed by registration number.
* :class:`AutotekaFullReport` — paid full report; idempotent so retries reuse
  the same ``Idempotency-Key`` and Avito does not double-debit.

Live tests are gated on ``AVITOAPI_LIVE=1`` (W6 ships only unit tests with
canned fixtures so CI never spends real money on a flaky webhook).

Naming: the DTO is imported as ``AutotekaFullReportDoc`` here to keep the
method-class name (``AutotekaFullReport``) aligned with the spec while
avoiding a symbol collision with the same-named model.
"""
from __future__ import annotations

from typing import ClassVar, Self

from pydantic import Field, model_validator

from ..models.autoteka import AutotekaFullReport as AutotekaFullReportDoc
from ..models.autoteka import AutotekaPreview
from ._base import BaseMethod


class AutotekaPreviewByVin(BaseMethod[AutotekaPreview]):
    """Free preview via ``GET /autoteka/v1/preview?vin=``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/autoteka/v1/preview"

    vin: str = Field(..., min_length=11, max_length=17, description="Vehicle VIN.")


class AutotekaPreviewByRegnum(BaseMethod[AutotekaPreview]):
    """Free preview via ``GET /autoteka/v1/preview?regnum=``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/autoteka/v1/preview"

    regnum: str = Field(..., min_length=4, description="Russian registration plate.")


class AutotekaFullReport(BaseMethod[AutotekaFullReportDoc]):
    """Paid full report via ``POST /autoteka/v1/report``.

    Wire shape: ``{"vin": "..."}`` OR ``{"regnum": "..."}`` — exactly one
    identifier per call. The validator enforces the XOR client-side so callers
    don't waste a paid round-trip on a 4xx.

    Idempotent mutation — same ``Idempotency-Key`` on retry, so Avito does
    not bill twice when a transport blip triggers a retry.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/autoteka/v1/report"
    __idempotent_mutation__: ClassVar[bool] = True

    vin: str | None = Field(default=None, min_length=11, max_length=17)
    regnum: str | None = Field(default=None, min_length=4)

    @model_validator(mode="after")
    def _exactly_one_identifier(self) -> Self:
        if (self.vin is None) == (self.regnum is None):
            raise ValueError("AutotekaFullReport requires exactly one of vin / regnum")
        return self
