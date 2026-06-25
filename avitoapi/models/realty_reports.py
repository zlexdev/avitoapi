"""Realty-reports domain — market-price correspondence + report tasks.

Two endpoints:

* :class:`MarketPriceCorrespondence` — synchronous answer surfaced by
  ``GET /realty/v1/marketPriceCorrespondence/{itemId}/{price}``.
* :class:`RealtyReportTask` — async-job handle returned by ``POST
  /realty/v1/report/create/{itemId}`` (real report shipped via a follow-up
  task-status surface that Avito doesn't yet expose).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from ._base import AvitoObject


class MarketPriceCorrespondence(BaseModel):
    """Answer to ``GET /realty/v1/marketPriceCorrespondence/{itemId}/{price}``.

    Avito returns a relative position (``below`` / ``within`` / ``above``)
    plus the market-median benchmark used to classify.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    item_id: int = Field(..., alias="itemId", description="Item the answer is for.")
    price: int = Field(..., description="Price the caller probed (integer rubles).")
    correspondence: str = Field(
        ...,
        description="Bucket name: ``below`` / ``within`` / ``above`` (forward-compat).",
    )
    market_median: int | None = Field(
        default=None,
        alias="marketMedian",
        description="Reference median, when surfaced.",
    )


class RealtyReportTask(AvitoObject):
    """Task handle returned by ``POST /realty/v1/report/create/{itemId}``."""


    task_id: str = Field(
        ...,
        alias="taskId",
        description="Server-side task id; poll via Avito's task-status surface.",
    )
    state: str = Field(
        default="pending",
        description="Initial state (``pending`` / ``running`` / ``done`` / ``failed``).",
    )
