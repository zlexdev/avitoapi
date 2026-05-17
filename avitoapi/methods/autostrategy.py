"""Autostrategy v1 — campaign lifecycle, daily budget, stats.

Avito's autostrategy product is REST-on-POST: every endpoint is ``POST`` with
a JSON body, including read-only fetches (``/info``, ``/campaigns``,
``/stat``). All write actions are flagged ``__idempotent_mutation__`` so the
funnel injects an ``Idempotency-Key`` and retries are safe.
"""

from __future__ import annotations

from datetime import date
from typing import ClassVar

from pydantic import Field

from ..models.autostrategy import (
    AutostrategyStatList,
    BudgetUpdateResult,
    CampaignActionResult,
    CampaignInfo,
    CampaignList,
)
from ..models.common import Money
from ._base import BaseMethod


class SetAutostrategyBudget(BaseMethod[BudgetUpdateResult]):
    """Set or update an autostrategy campaign's daily budget via
    ``POST /autostrategy/v1/budget``.

    Idempotent — the funnel injects an ``Idempotency-Key`` so retries do not
    apply the same budget twice.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/autostrategy/v1/budget"
    __idempotent_mutation__: ClassVar[bool] = True

    campaign_id: str = Field(..., min_length=1, description="Campaign whose budget is being set.")
    daily_budget: Money = Field(..., description="New daily-budget cap.")


class CreateAutostrategyCampaign(BaseMethod[CampaignActionResult]):
    """Create a new autostrategy campaign via
    ``POST /autostrategy/v1/campaign/create``.

    Idempotent — the funnel injects an ``Idempotency-Key`` so a retried call
    does not spawn a duplicate campaign.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/autostrategy/v1/campaign/create"
    __idempotent_mutation__: ClassVar[bool] = True

    name: str = Field(..., min_length=1, description="Human-readable campaign name.")
    daily_budget: Money = Field(..., description="Initial daily-budget cap.")
    item_ids: list[int] = Field(
        default_factory=list,
        description="Items targeted by the campaign (empty = all eligible items).",
    )
    category_ids: list[int] = Field(
        default_factory=list,
        description="Categories targeted by the campaign.",
    )
    regions: list[str] = Field(
        default_factory=list,
        description="Region slugs to restrict the campaign to.",
    )


class EditAutostrategyCampaign(BaseMethod[CampaignActionResult]):
    """Edit an existing autostrategy campaign via
    ``POST /autostrategy/v1/campaign/edit``.

    Idempotent — the funnel injects an ``Idempotency-Key`` so the same diff
    can be retried safely.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/autostrategy/v1/campaign/edit"
    __idempotent_mutation__: ClassVar[bool] = True

    campaign_id: str = Field(..., min_length=1, description="Campaign being edited.")
    name: str | None = Field(default=None, description="New name; omit to leave unchanged.")
    daily_budget: Money | None = Field(
        default=None,
        description="New daily budget; omit to leave unchanged.",
    )


class GetAutostrategyCampaignInfo(BaseMethod[CampaignInfo]):
    """Fetch the extended detail for one campaign via
    ``POST /autostrategy/v1/campaign/info`` (read-only, body-only routing).
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/autostrategy/v1/campaign/info"

    campaign_id: str = Field(..., min_length=1)


class StopAutostrategyCampaign(BaseMethod[CampaignActionResult]):
    """Stop an active campaign via ``POST /autostrategy/v1/campaign/stop``.

    Idempotent — retrying after a network blip does not bounce the state
    machine.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/autostrategy/v1/campaign/stop"
    __idempotent_mutation__: ClassVar[bool] = True

    campaign_id: str = Field(..., min_length=1)


class ListAutostrategyCampaigns(BaseMethod[CampaignList]):
    """List autostrategy campaigns via ``POST /autostrategy/v1/campaigns``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/autostrategy/v1/campaigns"

    page: int = Field(default=1, ge=1, description="1-based page number.")
    per_page: int = Field(default=25, ge=1, le=100, description="Page size (Avito caps at 100).")


class GetAutostrategyStats(BaseMethod[AutostrategyStatList]):
    """Fetch per-day campaign stats via ``POST /autostrategy/v1/stat``.

    The date window is inclusive on both ends; Avito's response is a flat
    list (one row per day).
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/autostrategy/v1/stat"

    campaign_id: str = Field(..., min_length=1)
    date_from: date = Field(..., description="Window start (inclusive).")
    date_to: date = Field(..., description="Window end (inclusive).")
