"""Balance-domain endpoints — real / bonus balance and operation history."""
from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from ..models.balance import Balance, BalanceBonus, Operation
from ..models.common import Page
from ..pagination import PageMethod
from ._base import BaseMethod


class GetBalance(BaseMethod[Balance]):
    """Real-money balance via ``GET /core/v1/accounts/{user_id}/balance/``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/core/v1/accounts/{user_id}/balance/"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id"})

    user_id: int = Field(..., ge=1)


class GetBalanceBonus(BaseMethod[BalanceBonus]):
    """Bonus balance via ``GET /core/v1/accounts/{user_id}/balance/bonus``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/core/v1/accounts/{user_id}/balance/bonus"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id"})

    user_id: int = Field(..., ge=1)


class OperationsHistory(PageMethod[Page[Operation]]):
    """Paginated wallet operations history via ``POST /core/v1/accounts/operations_history/``.

    Body fields = date range + page/per_page. Avito returns a page envelope.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/core/v1/accounts/operations_history/"

    date_from: datetime = Field(...)
    date_to: datetime = Field(...)
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=25, ge=1, le=100)
