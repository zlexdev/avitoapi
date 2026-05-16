"""Balance domain — real / bonus balance + operation history rows."""
from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator

from .common import Money


class Balance(BaseModel):
    """Real-money wallet balance returned by ``GET /core/v1/accounts/{user_id}/balance/``."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    real: Money = Field(..., description="Real-money balance (rubles).")
    as_of: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Snapshot timestamp; synthesised if Avito omits it from the body.",
    )

    @model_validator(mode="before")
    @classmethod
    def _ensure_as_of(cls, data: object) -> object:
        if isinstance(data, dict) and "as_of" not in data:
            data["as_of"] = datetime.now(UTC)
        return data


class BalanceBonus(BaseModel):
    """Bonus balance returned by ``GET /core/v1/accounts/{user_id}/balance/bonus``."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    bonus: Money = Field(..., description="Bonus-money balance (non-cashable).")


class OperationType(StrEnum):
    """Operation kind in the wallet history (extend as the API exposes more)."""

    REFILL = "refill"
    SPEND = "spend"
    REFUND = "refund"
    BONUS_AWARD = "bonus_award"
    HOLD = "hold"
    RELEASE = "release"


class Operation(BaseModel):
    """One row of the wallet operations history."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    id: str | int = Field(..., description="Stable operation id (string or numeric).")
    kind: OperationType = Field(..., description="Operation kind.")
    amount: Money = Field(..., description="Signed amount; positive=credit, negative=debit.")
    created_at: datetime = Field(..., description="Operation timestamp (UTC).")
    meta: dict[str, str] = Field(
        default_factory=dict,
        description="Free-form per-operation metadata (string values only).",
    )


class OperationList(RootModel[list[Operation]]):
    """Top-level JSON array envelope for endpoints that return a bare list of operations."""

    root: list[Operation] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)
