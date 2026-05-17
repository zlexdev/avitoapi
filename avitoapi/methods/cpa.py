"""CPA v3 — balance, calls/chats by time, complaints CRUD."""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from ..models.cpa import (
    CallList,
    ChatByTime,
    ChatList,
    Complaint,
    ComplaintList,
    CpaBalanceInfo,
)
from ..pagination import PageMethod
from ._base import BaseMethod


class CpaBalance(BaseMethod[CpaBalanceInfo]):
    """CPA balance via ``POST /cpa/v3/balanceInfo``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/cpa/v3/balanceInfo"


class CallsByTime(BaseMethod[CallList]):
    """CPA calls in a time window via ``POST /cpa/v3/callsByTime``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/cpa/v3/callsByTime"

    date_time_from: datetime = Field(..., description="Window start (UTC).")
    date_time_to: datetime = Field(..., description="Window end (UTC).")


class ChatsByTime(BaseMethod[ChatList]):
    """CPA chats in a time window via ``POST /cpa/v3/chatsByTime``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/cpa/v3/chatsByTime"

    date_time_from: datetime = Field(..., description="Window start (UTC).")
    date_time_to: datetime = Field(..., description="Window end (UTC).")


class ChatByActionId(BaseMethod[ChatByTime]):
    """One CPA chat by action id via ``POST /cpa/v3/chatByActionId``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/cpa/v3/chatByActionId"

    action_id: str = Field(..., min_length=1)


class ListComplaints(PageMethod[ComplaintList]):
    """List CPA complaints via ``GET /cpa/v3/complaints``.

    ``ComplaintList`` is a ``RootModel[list[Complaint]]`` — default extractor
    pulls items from ``.root``.
    """

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/cpa/v3/complaints"

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=25, ge=1, le=100)


class CreateComplaint(BaseMethod[Complaint]):
    """Create a CPA complaint via ``POST /cpa/v3/complaints``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/cpa/v3/complaints"
    __idempotent_mutation__: ClassVar[bool] = True

    action_id: str = Field(..., min_length=1)
    kind: str = Field(..., min_length=1, description="Complaint kind slug.")
    reason: str | None = Field(default=None, description="Free-form reason.")


class CancelComplaint(BaseMethod[None]):
    """Cancel a CPA complaint via ``POST /cpa/v3/complaints/{complaint_id}/cancel``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/cpa/v3/complaints/{complaint_id}/cancel"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"complaint_id"})
    __idempotent_mutation__: ClassVar[bool] = True

    complaint_id: str = Field(..., min_length=1)
