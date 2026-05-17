"""Autoteka — VIN/regnum previews + paid full report (offline fixtures only)."""

from __future__ import annotations

import json

import pytest
from avitoapi.client import Client
from avitoapi.methods.autoteka import (
    AutotekaFullReport,
    AutotekaPreviewByRegnum,
    AutotekaPreviewByVin,
)
from avitoapi.models.autoteka import AutotekaFullReport as AutotekaFullReportDoc
from avitoapi.models.autoteka import AutotekaPreview

from tests._fake_session import FakeSession


async def test_autoteka_preview_by_vin_returns_typed_preview(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(AutotekaPreviewByVin, "autoteka/preview.json")

    preview = await client(AutotekaPreviewByVin(vin="WVWZZZ1KZAW123456"))

    assert isinstance(preview, AutotekaPreview)
    assert preview.brand == "Volkswagen"
    assert preview.year == 2019
    assert preview.has_accidents is False


async def test_autoteka_preview_by_vin_carries_vin_in_query(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(AutotekaPreviewByVin, "autoteka/preview.json")

    await client(AutotekaPreviewByVin(vin="WVWZZZ1KZAW123456"))

    prepared = fake_session.sent[-1]
    assert prepared.http_method == "GET"
    assert prepared.url.endswith("/autoteka/v1/preview")
    assert prepared.query.get("vin") == "WVWZZZ1KZAW123456"


async def test_autoteka_preview_by_regnum_returns_typed_preview(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(AutotekaPreviewByRegnum, "autoteka/preview_regnum.json")

    preview = await client(AutotekaPreviewByRegnum(regnum="A123BC77"))

    assert isinstance(preview, AutotekaPreview)
    assert preview.regnum == "A123BC77"
    assert preview.has_accidents is True


async def test_autoteka_full_report_round_trip_with_vin(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(AutotekaFullReport, "autoteka/full_report.json")

    report = await client(AutotekaFullReport(vin="WVWZZZ1KZAW123456"))

    assert isinstance(report, AutotekaFullReportDoc)
    assert report.vin == "WVWZZZ1KZAW123456"
    assert report.summary["owners"] == 2
    assert "ownership" in report.sections


async def test_autoteka_full_report_emits_post_with_idempotency_key(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(AutotekaFullReport, "autoteka/full_report.json")

    await client(AutotekaFullReport(vin="WVWZZZ1KZAW123456"))

    prepared = fake_session.sent[-1]
    assert prepared.http_method == "POST"
    assert prepared.url.endswith("/autoteka/v1/report")
    assert "Idempotency-Key" in prepared.headers
    body = prepared.body if isinstance(prepared.body, dict) else json.loads(prepared.body)  # type: ignore[arg-type]
    assert body["vin"] == "WVWZZZ1KZAW123456"


def test_autoteka_full_report_rejects_both_identifiers() -> None:
    with pytest.raises(ValueError, match="exactly one"):
        AutotekaFullReport(vin="WVWZZZ1KZAW123456", regnum="A123BC77")


def test_autoteka_full_report_rejects_neither_identifier() -> None:
    with pytest.raises(ValueError, match="exactly one"):
        AutotekaFullReport()
