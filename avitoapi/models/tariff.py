"""Tariff domain — current subscription plan, quotas, expiry."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from ._base import AvitoObject


class TariffInfo(AvitoObject):
    """Result of ``GET /tariff/info/1`` — current subscription snapshot.

    Avito surfaces the plan name, the active feature set under ``limits``,
    and an optional expiry. Unknown keys land in ``extra`` (forward-compat).
    """


    name: str | None = Field(default=None, description="Human-readable tariff name.")
    plan: str | None = Field(default=None, description="Internal plan code.")
    limits: dict[str, Any] = Field(
        default_factory=dict,
        description="Per-feature quotas keyed by feature name.",
    )
    expires_at: datetime | None = Field(
        default=None,
        alias="expiresAt",
        description="Subscription expiry (UTC); ``None`` for evergreen plans.",
    )
