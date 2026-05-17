"""Stats domain — per-item view / contact / call analytics rows."""

from __future__ import annotations

from datetime import date as _Date

from pydantic import BaseModel, ConfigDict, Field, RootModel


class ItemViewStats(BaseModel):
    """One row of per-item stats from ``/stats/v1/.../items/shallow`` or deep variant."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    item_id: int = Field(..., description="Avito item id this row aggregates.")
    views: int = Field(default=0, ge=0, description="Total views in the window.")
    contacts: int = Field(default=0, ge=0, description="Total contact actions in the window.")
    favorites: int = Field(default=0, ge=0, description="Times added to favourites in the window.")
    date: _Date | None = Field(
        default=None,
        description="Window day; absent for aggregated (non-daily) responses.",
    )


class CallStat(BaseModel):
    """One row of per-item call stats from ``/stats/v1/.../items/{item_id}/calls``."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    item_id: int = Field(..., description="Item id this row belongs to.")
    calls: int = Field(..., ge=0, description="Number of inbound calls on the day.")
    date: _Date = Field(..., description="Date the calls were counted for.")


class ItemViewStatsList(RootModel[list[ItemViewStats]]):
    """Top-level JSON array envelope for shallow/deep stats responses."""

    root: list[ItemViewStats] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class CallStatList(RootModel[list[CallStat]]):
    """Top-level JSON array envelope for call-stats responses."""

    root: list[CallStat] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)
