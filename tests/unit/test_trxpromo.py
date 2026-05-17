"""TrxPromo v1 — apply / cancel / commissions round-trips."""

from __future__ import annotations

import json
from datetime import date

from avitoapi.client import Client
from avitoapi.methods.trxpromo import (
    ApplyTrxPromo,
    CancelTrxPromo,
    GetTrxCommissions,
)
from avitoapi.models.trxpromo import (
    TrxApplyResult,
    TrxCancelResult,
    TrxCommissionList,
)

from tests._fake_session import FakeSession


async def test_apply_trx_promo_idempotent(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ApplyTrxPromo, "trxpromo/apply_result.json")

    result = await client(ApplyTrxPromo(promo_code="SUMMER26", category_ids=[42]))

    assert isinstance(result, TrxApplyResult)
    assert result.promo_id == "trx_abc123"
    assert result.ok is True
    prepared = fake_session.sent[-1]
    assert prepared.http_method == "POST"
    assert prepared.url.endswith("/trx-promo/1/apply")
    assert "Idempotency-Key" in prepared.headers
    body = prepared.body if isinstance(prepared.body, dict) else json.loads(prepared.body)
    assert body["promo_code"] == "SUMMER26"
    assert body["category_ids"] == [42]


async def test_cancel_trx_promo_idempotent(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(CancelTrxPromo, "trxpromo/cancel_result.json")

    result = await client(CancelTrxPromo(promo_id="trx_abc123"))

    assert isinstance(result, TrxCancelResult)
    assert result.promo_id == "trx_abc123"
    assert result.ok is True
    prepared = fake_session.sent[-1]
    assert prepared.url.endswith("/trx-promo/1/cancel")
    assert "Idempotency-Key" in prepared.headers


async def test_get_trx_commissions_decodes_rules(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetTrxCommissions, "trxpromo/commissions.json")

    rules = await client(GetTrxCommissions())

    assert isinstance(rules, TrxCommissionList)
    assert len(rules) == 2
    rows = list(rules)
    assert rows[0].category_id == 42
    assert rows[0].commission_pct == 5.5
    assert rows[0].effective_from == date(2026, 1, 1)
    assert rows[1].effective_from is None
    prepared = fake_session.sent[-1]
    assert prepared.http_method == "GET"
    assert prepared.url.endswith("/trx-promo/1/commissions")
