"""Autostrategy v1 — budget, campaign CRUD, info, stats round-trips."""
from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

from avitoapi.client import Client
from avitoapi.methods.autostrategy import (
    CreateAutostrategyCampaign,
    EditAutostrategyCampaign,
    GetAutostrategyCampaignInfo,
    GetAutostrategyStats,
    ListAutostrategyCampaigns,
    SetAutostrategyBudget,
    StopAutostrategyCampaign,
)
from avitoapi.models.autostrategy import (
    AutostrategyStatList,
    BudgetUpdateResult,
    CampaignActionResult,
    CampaignInfo,
    CampaignList,
    CampaignStatus,
)
from avitoapi.models.common import Currency, Money

from tests._fake_session import FakeSession


async def test_set_autostrategy_budget_idempotent(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(SetAutostrategyBudget, "autostrategy/budget_update.json")

    result = await client(
        SetAutostrategyBudget(
            campaign_id="as_001",
            daily_budget=Money(amount=Decimal("2000"), currency=Currency.RUB),
        ),
    )

    assert isinstance(result, BudgetUpdateResult)
    assert result.campaign_id == "as_001"
    prepared = fake_session.sent[-1]
    assert prepared.http_method == "POST"
    assert prepared.url.endswith("/autostrategy/v1/budget")
    assert "Idempotency-Key" in prepared.headers
    body = prepared.body if isinstance(prepared.body, dict) else json.loads(prepared.body)
    assert body["campaign_id"] == "as_001"
    assert body["daily_budget"]["amount"] == "2000"


async def test_create_autostrategy_campaign_idempotent(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(CreateAutostrategyCampaign, "autostrategy/action_result.json")

    result = await client(
        CreateAutostrategyCampaign(
            name="Premium Campaign",
            daily_budget=Money(amount=Decimal("1500"), currency=Currency.RUB),
            item_ids=[9001, 9002],
        ),
    )

    assert isinstance(result, CampaignActionResult)
    assert result.campaign_id == "as_001"
    assert result.ok is True
    prepared = fake_session.sent[-1]
    assert prepared.url.endswith("/autostrategy/v1/campaign/create")
    assert "Idempotency-Key" in prepared.headers
    body = prepared.body if isinstance(prepared.body, dict) else json.loads(prepared.body)
    assert body["name"] == "Premium Campaign"
    assert body["item_ids"] == [9001, 9002]


async def test_edit_autostrategy_campaign_idempotent(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(EditAutostrategyCampaign, "autostrategy/action_result.json")

    result = await client(
        EditAutostrategyCampaign(campaign_id="as_001", name="New Name"),
    )

    assert isinstance(result, CampaignActionResult)
    prepared = fake_session.sent[-1]
    assert prepared.url.endswith("/autostrategy/v1/campaign/edit")
    assert "Idempotency-Key" in prepared.headers


async def test_get_autostrategy_campaign_info_decodes_extended(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetAutostrategyCampaignInfo, "autostrategy/campaign_info.json")

    info = await client(GetAutostrategyCampaignInfo(campaign_id="as_001"))

    assert isinstance(info, CampaignInfo)
    assert info.id == "as_001"
    assert info.status is CampaignStatus.ACTIVE
    assert info.budget is not None
    assert info.budget.spent_today is not None
    assert info.budget.spent_today.amount == Decimal("320.50")
    assert info.targeting is not None
    assert info.targeting.item_ids == [9001, 9002, 9003]


async def test_stop_autostrategy_campaign_idempotent(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(StopAutostrategyCampaign, "autostrategy/action_result.json")

    result = await client(StopAutostrategyCampaign(campaign_id="as_001"))

    assert isinstance(result, CampaignActionResult)
    prepared = fake_session.sent[-1]
    assert prepared.url.endswith("/autostrategy/v1/campaign/stop")
    assert "Idempotency-Key" in prepared.headers


async def test_list_autostrategy_campaigns_decodes_list(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ListAutostrategyCampaigns, "autostrategy/campaigns.json")

    campaigns = await client(ListAutostrategyCampaigns())

    assert isinstance(campaigns, CampaignList)
    assert len(campaigns) == 2
    rows = list(campaigns)
    assert rows[0].id == "as_001"
    assert rows[0].status is CampaignStatus.ACTIVE
    assert rows[1].status is CampaignStatus.DRAFT


async def test_get_autostrategy_stats_decodes_rows(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetAutostrategyStats, "autostrategy/stats.json")

    stats = await client(
        GetAutostrategyStats(
            campaign_id="as_001",
            date_from=date(2026, 5, 14),
            date_to=date(2026, 5, 15),
        ),
    )

    assert isinstance(stats, AutostrategyStatList)
    assert len(stats) == 2
    rows = list(stats)
    assert rows[0].date == date(2026, 5, 14)
    assert rows[0].impressions == 12500
    assert rows[1].clicks == 421
    prepared = fake_session.sent[-1]
    assert prepared.url.endswith("/autostrategy/v1/stat")


async def test_campaign_bound_methods_target_correct_endpoints(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetAutostrategyCampaignInfo, "autostrategy/campaign_info.json")
    fake_session.bind_fixture(StopAutostrategyCampaign, "autostrategy/action_result.json")

    info = await client(GetAutostrategyCampaignInfo(campaign_id="as_001"))

    stop_call = info.stop()
    await stop_call

    prepared = fake_session.sent[-1]
    assert prepared.url.endswith("/autostrategy/v1/campaign/stop")
    body = prepared.body if isinstance(prepared.body, dict) else json.loads(prepared.body)
    assert body["campaign_id"] == "as_001"
