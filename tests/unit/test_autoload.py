"""Autoload domain — method-class fixture round-trips + binary upload routing."""

from __future__ import annotations

import json
from typing import Any

from avitoapi.client import Client
from avitoapi.methods.autoload import (
    AutoloadItemStatus,
    ConvertAutoloadId,
    GetAutoloadCategoryFields,
    GetAutoloadProfile,
    GetAutoloadReport,
    GetLastAutoloadReport,
    ListAutoloadReports,
    UpdateAutoloadProfile,
    UploadAutoloadFile,
)
from avitoapi.models.autoload import (
    AutoloadCategoryFields,
    AutoloadIdConversion,
    AutoloadItemReport,
    AutoloadProfile,
    AutoloadReport,
    AutoloadUploadResult,
)
from avitoapi.models.autoload import (
    AutoloadItemStatus as ItemStatusEnum,
)
from avitoapi.models.common import Page

from tests._fake_session import FakeSession

# ---- per-item status -------------------------------------------------------


async def test_autoload_item_status_returns_typed_report(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(AutoloadItemStatus, "autoload/item_report.json")

    report = await client(AutoloadItemStatus(user_id=42, ad_id=9876543))

    assert isinstance(report, AutoloadItemReport)
    assert report.ad_id == 9876543
    assert report.status is ItemStatusEnum.SUCCESS


async def test_autoload_item_status_uses_path_template(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(AutoloadItemStatus, "autoload/item_report.json")

    await client(AutoloadItemStatus(user_id=42, ad_id=9876543))

    prepared = fake_session.sent[-1]
    assert prepared.http_method == "GET"
    assert prepared.url.endswith("/autoload/v1/accounts/42/items/9876543/")


# ---- reports page ----------------------------------------------------------


async def test_list_autoload_reports_returns_page_envelope(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ListAutoloadReports, "autoload/reports_page.json")

    page = await client(ListAutoloadReports(user_id=42, page=1, per_page=25))

    assert isinstance(page, Page)
    assert page.total == 1
    assert len(page.items) == 1
    assert page.items[0].id == "report-2026-05-15"


async def test_get_last_autoload_report_round_trip(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetLastAutoloadReport, "autoload/report.json")

    report = await client(GetLastAutoloadReport(user_id=42))

    assert isinstance(report, AutoloadReport)
    assert report.total == 120
    assert report.errors == 2
    assert len(report.items) == 2
    assert report.items[1].status is ItemStatusEnum.ERROR


async def test_get_autoload_report_uses_report_id_in_path(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetAutoloadReport, "autoload/report.json")

    await client(GetAutoloadReport(user_id=42, report_id="report-2026-05-16"))

    prepared = fake_session.sent[-1]
    assert prepared.url.endswith("/autoload/v1/accounts/42/reports/report-2026-05-16/")


# ---- category fields -------------------------------------------------------


async def test_get_autoload_category_fields_returns_typed_schema(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetAutoloadCategoryFields, "autoload/category_fields.json")

    schema = await client(GetAutoloadCategoryFields(category_id=5))

    assert isinstance(schema, AutoloadCategoryFields)
    assert "title" in schema.required
    assert "video_url" in schema.optional


# ---- profile get / update --------------------------------------------------


async def test_get_autoload_profile_returns_dto(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetAutoloadProfile, "autoload/profile.json")

    profile = await client(GetAutoloadProfile())

    assert isinstance(profile, AutoloadProfile)
    assert profile.feed_url is not None
    assert profile.format == "xml"


async def test_update_autoload_profile_emits_put_with_idempotency_key(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(UpdateAutoloadProfile, "autoload/profile.json")

    await client(
        UpdateAutoloadProfile(
            feed_url="https://seller.example.com/feed.xml",
            schedule="0 */6 * * *",
            format="xml",
        ),
    )

    prepared = fake_session.sent[-1]
    assert prepared.http_method == "PUT"
    assert prepared.url.endswith("/autoload/v1/profile")
    assert "Idempotency-Key" in prepared.headers
    body = prepared.body if isinstance(prepared.body, dict) else json.loads(prepared.body)  # type: ignore[arg-type]
    assert body["feed_url"] == "https://seller.example.com/feed.xml"


# ---- upload ----------------------------------------------------------------


async def test_upload_autoload_file_carries_bytes_in_body(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(UploadAutoloadFile, "autoload/upload_result.json")
    payload = b"<feed><item id='1'/></feed>"

    result = await client(UploadAutoloadFile(filename="feed.xml", file_bytes=payload))

    assert isinstance(result, AutoloadUploadResult)
    assert result.accepted is True
    prepared = fake_session.sent[-1]
    assert prepared.http_method == "POST"
    assert prepared.url.endswith("/autoload/v1/upload")
    # bytes are base64-encoded by the JSON dump (Wave-6 simplification, same as W3 SendImageMessage)
    body: Any = prepared.body if isinstance(prepared.body, dict) else json.loads(prepared.body)  # type: ignore[arg-type]
    assert body["filename"] == "feed.xml"
    assert "file_bytes" in body


# ---- id conversion ---------------------------------------------------------


async def test_convert_autoload_id_unpacks_top_level_mapping(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ConvertAutoloadId, "autoload/convert.json")

    conv = await client(ConvertAutoloadId(ad_id="seller-sku-123"))

    assert isinstance(conv, AutoloadIdConversion)
    assert conv.mapping["seller-sku-123"] == 9876543
