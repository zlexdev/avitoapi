"""Autostrategy domain — campaign DTOs, budget config, stats rows.

Autostrategy is Avito's automated-bidding promotion product: the seller sets
a daily budget and the platform picks per-item bids. The domain exposes the
campaign lifecycle (create / edit / stop / info / list), the daily budget
write, and a stats endpoint returning per-day rows.

Response DTOs use ``ConfigDict(strict=False, extra="allow")`` — Avito's
schemas drift faster than this module can be refreshed, matching the W5/W6
forward-compat stance.
"""
from __future__ import annotations

from collections.abc import Iterator
from datetime import date as date_t
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, RootModel

from ._base import BoundModel
from .common import Money

if TYPE_CHECKING:
    from ..methods.autostrategy import (
        EditAutostrategyCampaign,
        GetAutostrategyCampaignInfo,
        GetAutostrategyStats,
        StopAutostrategyCampaign,
    )


class CampaignStatus(StrEnum):
    """Autostrategy campaign lifecycle states."""

    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    DRAFT = "draft"


class Campaign(BoundModel):
    """One autostrategy campaign row (list + info responses).

    Bound methods build awaitable method-classes pre-attached to the client;
    manually constructed campaigns (no client) raise
    :class:`~avitoapi.exceptions.ModelNotBoundError` on those actions.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    id: str = Field(..., description="Campaign identifier (string).")
    name: str = Field(..., description="Human-readable campaign name.")
    status: CampaignStatus = Field(..., description="Current lifecycle status.")
    daily_budget: Money | None = Field(
        default=None,
        description="Daily budget cap; absent on drafts.",
    )
    created_at: datetime | None = Field(default=None, description="Creation timestamp (UTC).")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp (UTC).")

    def edit(
        self,
        *,
        name: str | None = None,
        daily_budget: Money | None = None,
    ) -> EditAutostrategyCampaign:
        """Build an awaitable edit method-class bound to this campaign."""
        from ..methods.autostrategy import EditAutostrategyCampaign

        client = self._require_client()
        return EditAutostrategyCampaign(
            campaign_id=self.id,
            name=name,
            daily_budget=daily_budget,
        ).as_(client)

    def stop(self) -> StopAutostrategyCampaign:
        """Build an awaitable stop method-class bound to this campaign."""
        from ..methods.autostrategy import StopAutostrategyCampaign

        client = self._require_client()
        return StopAutostrategyCampaign(campaign_id=self.id).as_(client)

    def info(self) -> GetAutostrategyCampaignInfo:
        """Build an awaitable detail-fetch method-class bound to this campaign."""
        from ..methods.autostrategy import GetAutostrategyCampaignInfo

        client = self._require_client()
        return GetAutostrategyCampaignInfo(campaign_id=self.id).as_(client)

    def stats(
        self,
        date_from: date_t,
        date_to: date_t,
    ) -> GetAutostrategyStats:
        """Build an awaitable stats method-class for this campaign over a date window."""
        from ..methods.autostrategy import GetAutostrategyStats

        client = self._require_client()
        return GetAutostrategyStats(
            campaign_id=self.id,
            date_from=date_from,
            date_to=date_to,
        ).as_(client)


class CampaignList(RootModel[list[Campaign]]):
    """Top-level JSON array envelope for the campaign-list response."""

    root: list[Campaign] = Field(default_factory=list)

    def __iter__(self) -> Iterator[Campaign]:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class CampaignTargeting(BaseModel):
    """Targeting block surfaced by ``GetAutostrategyCampaignInfo``.

    Forward-compatible: Avito ships new targeting axes (geo, category, item
    subset) on its own schedule; ``extra="allow"`` preserves unknown keys.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    item_ids: list[int] = Field(default_factory=list, description="Items the campaign targets.")
    category_ids: list[int] = Field(
        default_factory=list,
        description="Avito category ids included in the campaign.",
    )
    regions: list[str] = Field(
        default_factory=list,
        description="Region slugs the campaign is restricted to.",
    )


class CampaignBudgetBreakdown(BaseModel):
    """Per-day budget accounting returned alongside the campaign detail."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    daily_budget: Money | None = Field(default=None, description="Configured daily budget cap.")
    spent_today: Money | None = Field(default=None, description="Amount spent so far today.")
    spent_total: Money | None = Field(default=None, description="Lifetime spend on this campaign.")
    remaining_today: Money | None = Field(
        default=None,
        description="Today's remaining budget — convenience field.",
    )


class CampaignInfo(Campaign):
    """Extended campaign detail returned by ``GetAutostrategyCampaignInfo``.

    Inherits :class:`Campaign` (same id/name/status/timestamps), and adds the
    budget breakdown + targeting envelope Avito surfaces on the detail call.
    """

    budget: CampaignBudgetBreakdown | None = Field(
        default=None,
        description="Budget accounting; absent on freshly-created drafts.",
    )
    targeting: CampaignTargeting | None = Field(
        default=None,
        description="Targeting block (items / categories / regions).",
    )


class BudgetUpdateResult(BaseModel):
    """Acknowledgement DTO for ``SetAutostrategyBudget``.

    Avito returns a thin echo of the applied budget plus a server timestamp;
    extra keys are preserved for forward compatibility.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    campaign_id: str | None = Field(default=None, description="Campaign the budget was applied to.")
    daily_budget: Money | None = Field(default=None, description="Applied daily-budget value.")
    applied_at: datetime | None = Field(default=None, description="Server timestamp of the update.")


class CampaignActionResult(BaseModel):
    """Acknowledgement DTO for create / edit / stop campaign endpoints.

    Avito's response varies by action (create returns the new id, edit
    returns the campaign echo, stop returns just an ok flag); the union
    here is permissive on purpose.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    campaign_id: str | None = Field(default=None, description="Affected campaign id.")
    status: CampaignStatus | None = Field(default=None, description="Resulting status, when surfaced.")
    ok: bool | None = Field(default=None, description="Server-side success flag, when surfaced.")


class AutostrategyStat(BaseModel):
    """One per-day stats row returned by ``GetAutostrategyStats``."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    date: date_t = Field(..., description="Stats day (UTC).")
    spent: Money | None = Field(default=None, description="Amount spent on the day.")
    impressions: int | None = Field(default=None, ge=0, description="Ad impressions count.")
    clicks: int | None = Field(default=None, ge=0, description="Click count.")
    contacts: int | None = Field(default=None, ge=0, description="Buyer-contact count.")


class AutostrategyStatList(RootModel[list[AutostrategyStat]]):
    """Top-level JSON array envelope for the autostrategy stats response."""

    root: list[AutostrategyStat] = Field(default_factory=list)

    def __iter__(self) -> Iterator[AutostrategyStat]:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)
