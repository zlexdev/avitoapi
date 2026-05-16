"""Stock-management endpoints — bulk inventory probe + bulk update.

Two methods. Both are POST/PUT — :class:`GetStockInfo` is POST despite
being a read because Avito accepts a bulk list of item ids in the body;
:class:`UpdateStocks` is a PUT idempotent mutation.
"""
from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..models.stock_management import StockInfo, StockInfoList, StockUpdateResult
from ._base import BaseMethod


class GetStockInfo(BaseMethod[StockInfoList]):
    """Bulk inventory probe via ``POST /stock-management/1/info``.

    Args:
        item_ids: Ids to probe (Avito accepts up to 200 per call).
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/stock-management/1/info"

    item_ids: list[int] = Field(..., min_length=1, max_length=200)


class UpdateStocks(BaseMethod[StockUpdateResult]):
    """Bulk inventory update via ``PUT /stock-management/1/stocks``.

    Idempotent — same payload + same idempotency key = same outcome.
    """

    __http_method__: ClassVar[str] = "PUT"
    __endpoint__: ClassVar[str] = "/stock-management/1/stocks"
    __idempotent_mutation__: ClassVar[bool] = True

    stocks: list[StockInfo] = Field(
        ...,
        min_length=1,
        description="Replacement set of stock rows (full list, not a delta).",
    )
