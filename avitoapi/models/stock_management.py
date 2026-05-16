"""Stock-management domain — per-item inventory rows + bulk update result."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, RootModel

from ._base import BoundModel


class StockInfo(BaseModel):
    """One inventory row for a specific item / warehouse pair."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    item_id: int = Field(..., alias="itemId", description="Avito numeric item id.")
    warehouse_id: str | None = Field(
        default=None,
        alias="warehouseId",
        description="Warehouse id; ``None`` for single-warehouse sellers.",
    )
    in_stock: int = Field(
        ...,
        alias="inStock",
        ge=0,
        description="Units currently on hand.",
    )
    reserved: int = Field(
        default=0,
        ge=0,
        description="Units reserved by open orders.",
    )


class StockInfoList(RootModel[list[StockInfo]], BoundModel):
    """Top-level array envelope for stock-info responses."""

    root: list[StockInfo] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class StockUpdateResult(BoundModel):
    """Acknowledgement returned by ``PUT /stock-management/1/stocks``."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    success: bool = Field(default=True, description="True on 2xx.")
    updated: int | None = Field(
        default=None,
        description="Count of rows accepted; surfaced when Avito reports it.",
    )
    errors: list[dict[str, str]] = Field(
        default_factory=list,
        description="Per-row error details, when partial failures occur.",
    )
