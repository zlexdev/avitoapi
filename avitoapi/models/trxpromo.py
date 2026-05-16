"""TrxPromo domain — transaction-based promotion discount.

The TrxPromo product applies a discount on the per-transaction commission
Avito charges sellers, configurable per category. The domain exposes the
commission-rules listing plus the apply / cancel actions.

Response DTOs use ``ConfigDict(strict=False, extra="allow")`` — schemas are
sparsely documented and Avito ships fields on its own schedule.
"""
from __future__ import annotations

from collections.abc import Iterator
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, RootModel


class TrxCommissionRule(BaseModel):
    """One per-category commission rule returned by ``GetTrxCommissions``."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    category_id: int = Field(..., ge=1, description="Avito category the rule applies to.")
    commission_pct: float = Field(
        ...,
        ge=0,
        le=100,
        description="Commission percentage (0-100); float because Avito surfaces non-integer rates.",
    )
    effective_from: date | None = Field(
        default=None,
        description="Window start (inclusive); absent when the rule has no start gate.",
    )
    effective_to: date | None = Field(
        default=None,
        description="Window end (inclusive); absent when the rule is open-ended.",
    )


class TrxCommissionList(RootModel[list[TrxCommissionRule]]):
    """Top-level JSON array envelope for the commission-rules response."""

    root: list[TrxCommissionRule] = Field(default_factory=list)

    def __iter__(self) -> Iterator[TrxCommissionRule]:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class TrxApplyResult(BaseModel):
    """Acknowledgement DTO for ``ApplyTrxPromo``.

    Avito returns the activated promo id plus the time-window the discount
    is active on; ``extra="allow"`` preserves unknown keys.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    promo_id: str | None = Field(default=None, description="Identifier of the activated promo.")
    applied_at: datetime | None = Field(default=None, description="Server-side activation timestamp.")
    expires_at: datetime | None = Field(
        default=None,
        description="When the discount window closes; absent for open-ended promos.",
    )
    ok: bool | None = Field(default=None, description="Aggregate success flag, when surfaced.")


class TrxCancelResult(BaseModel):
    """Acknowledgement DTO for ``CancelTrxPromo``."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    promo_id: str | None = Field(default=None, description="Identifier of the cancelled promo.")
    cancelled_at: datetime | None = Field(default=None, description="Server-side cancellation timestamp.")
    ok: bool | None = Field(default=None, description="Aggregate success flag, when surfaced.")
