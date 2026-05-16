"""Autoload-domain endpoints — per-item status, reports, profile, feed upload.

Mutating method-classes (``UpdateAutoloadProfile``, ``UploadAutoloadFile``)
declare ``__idempotent_mutation__ = True`` so :class:`RestProtocol`
auto-injects an ``Idempotency-Key`` header.

``UploadAutoloadFile`` currently ships the feed bytes inside the JSON
body. ``__multipart__ = True`` is declared for the future multipart-aware
Protocol/Session pair.
"""
from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..models.autoload import (
    AutoloadCategoryFields,
    AutoloadIdConversion,
    AutoloadItemReport,
    AutoloadProfile,
    AutoloadReport,
    AutoloadUploadResult,
)
from ..models.common import Page
from ._base import BaseMethod


class AutoloadItemStatus(BaseMethod[AutoloadItemReport]):
    """Per-item upload state via ``GET /autoload/v1/accounts/{user_id}/items/{ad_id}/``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/autoload/v1/accounts/{user_id}/items/{ad_id}/"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id", "ad_id"})

    user_id: int = Field(..., ge=1)
    ad_id: int = Field(..., ge=1)


class ListAutoloadReports(BaseMethod[Page[AutoloadReport]]):
    """Paginated autoload-run reports via ``GET /autoload/v1/accounts/{user_id}/reports/``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/autoload/v1/accounts/{user_id}/reports/"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id"})

    user_id: int = Field(..., ge=1)
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=25, ge=1, le=100)


class GetLastAutoloadReport(BaseMethod[AutoloadReport]):
    """Most recent autoload-run report via ``GET .../reports/last_report/``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = (
        "/autoload/v1/accounts/{user_id}/reports/last_report/"
    )
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id"})

    user_id: int = Field(..., ge=1)


class GetAutoloadReport(BaseMethod[AutoloadReport]):
    """One autoload-run report by id via ``GET .../reports/{report_id}/``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = (
        "/autoload/v1/accounts/{user_id}/reports/{report_id}/"
    )
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id", "report_id"})

    user_id: int = Field(..., ge=1)
    report_id: str = Field(..., min_length=1)


class GetAutoloadCategoryFields(BaseMethod[AutoloadCategoryFields]):
    """Required + optional feed fields per category via the v2 fields endpoint."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/autoload/v2/items/category/{category_id}/fields"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"category_id"})

    category_id: int = Field(..., ge=1)


class GetAutoloadProfile(BaseMethod[AutoloadProfile]):
    """Read autoload profile via ``GET /autoload/v1/profile``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/autoload/v1/profile"


class UpdateAutoloadProfile(BaseMethod[AutoloadProfile]):
    """Persist autoload profile via ``PUT /autoload/v1/profile``.

    Idempotent mutation — auto-injects an ``Idempotency-Key`` header so retries
    don't reapply the same profile twice on flaky networks.
    """

    __http_method__: ClassVar[str] = "PUT"
    __endpoint__: ClassVar[str] = "/autoload/v1/profile"
    __idempotent_mutation__: ClassVar[bool] = True

    feed_url: str | None = Field(default=None)
    schedule: str | None = Field(default=None)
    format: str = Field(default="xml")


class UploadAutoloadFile(BaseMethod[AutoloadUploadResult]):
    """Upload a feed file via ``POST /autoload/v1/upload``.

    File bytes currently travel inside the JSON body (base64-encoded).
    ``__multipart__ = True`` is declared for the future multipart-aware
    Protocol/Session pair.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/autoload/v1/upload"
    __idempotent_mutation__: ClassVar[bool] = True
    __multipart__: ClassVar[bool] = True

    filename: str = Field(..., min_length=1, description="Original feed file name.")
    file_bytes: bytes = Field(
        ...,
        description="Raw feed bytes (XML / CSV); encoded for the wire by the session layer.",
    )


class ConvertAutoloadId(BaseMethod[AutoloadIdConversion]):
    """Convert seller-side ad id to Avito-side id via ``GET /autoload/v1/convert``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/autoload/v1/convert"

    ad_id: str = Field(..., min_length=1, description="Seller-side ad id from the feed.")
