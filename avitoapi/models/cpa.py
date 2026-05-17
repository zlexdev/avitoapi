"""CPA v3 domain — balance, calls/chats by time, complaints lifecycle."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, RootModel

from ._base import BoundModel
from .common import Money

if TYPE_CHECKING:
    from ..methods.cpa import CancelComplaint


class CpaBalanceInfo(BaseModel):
    """Balance breakdown returned by ``POST /cpa/v3/balanceInfo``."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    real: Money = Field(..., description="Real money balance.")
    bonus: Money = Field(..., description="Bonus money balance.")


class CallByTime(BaseModel):
    """One row from ``POST /cpa/v3/callsByTime``."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    action_id: str = Field(..., description="CPA action id (use for complaint linking).")
    item_id: int = Field(..., ge=1, description="Item the call was made about.")
    phone: str | None = Field(default=None, description="Caller's masked phone, when surfaced.")
    created_at: datetime = Field(..., description="Call timestamp (UTC).")
    duration_s: int | None = Field(default=None, ge=0, description="Call duration in seconds.")


class ChatByTime(BoundModel):
    """One row from ``POST /cpa/v3/chatsByTime`` (also the shape of ``chatByActionId``)."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    action_id: str = Field(..., description="CPA action id.")
    chat_id: str = Field(..., description="Messenger chat id this CPA action references.")
    item_id: int = Field(..., ge=1, description="Item the chat was started about.")
    created_at: datetime = Field(..., description="Chat-start timestamp (UTC).")


class ComplaintStatus(StrEnum):
    """Lifecycle states of a CPA complaint."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class Complaint(BoundModel):
    """One CPA complaint row + lifecycle."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    id: str = Field(..., description="Complaint id.")
    action_id: str = Field(..., description="CPA action this complaint references.")
    kind: str = Field(..., description="Complaint kind slug (Avito-defined enum).")
    status: ComplaintStatus = Field(..., description="Current lifecycle status.")
    created_at: datetime = Field(..., description="Creation timestamp (UTC).")
    reason: str | None = Field(default=None, description="Free-form reason, when supplied.")

    def cancel(self) -> CancelComplaint:
        """Build a cancel method-class bound to this complaint."""

        from ..methods.cpa import CancelComplaint

        client = self._require_client()
        return CancelComplaint(complaint_id=self.id).as_(client)


class CallList(RootModel[list[CallByTime]]):
    """Top-level array envelope for the calls-by-time response."""

    root: list[CallByTime] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class ChatList(RootModel[list[ChatByTime]], BoundModel):
    """Top-level array envelope for the chats-by-time response.

    Inherits :class:`BoundModel` so the funnel cascades the client into each
    contained :class:`ChatByTime`.
    """

    root: list[ChatByTime] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class ComplaintList(RootModel[list[Complaint]], BoundModel):
    """Top-level array envelope for the complaints listing.

    Inherits :class:`BoundModel` so the funnel cascades the client into each
    contained :class:`Complaint` (enabling ``complaint.cancel()``).
    """

    root: list[Complaint] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)
