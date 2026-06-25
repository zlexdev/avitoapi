"""Cross-domain value objects: Money, Page envelopes, error body."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Generic, TypeVar

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, field_serializer, field_validator


class Currency(StrEnum):
    """ISO-4217 currency codes Avito surfaces in payloads (extend as needed)."""

    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class Money(BaseModel):
    """A monetary amount with explicit currency. Amount is :class:`Decimal`, never ``float``."""

    model_config = ConfigDict(strict=True, frozen=True)

    amount: Decimal = Field(..., description="Decimal amount; serialized as string at the wire.")
    currency: Currency = Field(default=Currency.RUB, description="ISO-4217 currency code.")

    @field_validator("amount", mode="before")
    @classmethod
    def _coerce_amount(cls, value: object) -> object:
        if isinstance(value, float):
            return Decimal(str(value))
        if isinstance(value, str):
            # Wire format is a string (`format(amount, "f")`); accept it back symmetrically.
            return Decimal(value)
        if isinstance(value, int):
            return Decimal(value)
        return value

    @field_serializer("amount", when_used="json")
    def _serialize_amount(self, amount: Decimal) -> str:
        return format(amount, "f")


T = TypeVar("T", bound=BaseModel)


class Page(BaseModel, Generic[T]):
    """Page-of-results envelope returned by ``page``/``per_page`` endpoints."""

    model_config = ConfigDict(populate_by_name=True, strict=True)

    items: list[T] = Field(default_factory=list)
    page: int = Field(..., ge=1)
    per_page: int = Field(..., ge=1)
    total: int | None = Field(default=None, ge=0)


class AvitoErrorBody(BaseModel):
    """Common Avito error payload (``{"error": {"code": ..., "message": ...}}``)."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    code: str | int | None = None
    message: str | None = None


def _require_tz(v: datetime) -> datetime:
    """Reject naive datetimes — every wire datetime must carry timezone info."""
    if v.tzinfo is None:
        raise ValueError(f"datetime must be timezone-aware; got naive: {v!r}")
    return v


TZDatetime = Annotated[datetime, AfterValidator(_require_tz)]
"""``datetime`` subtype that rejects naive instances at Pydantic validation time."""
