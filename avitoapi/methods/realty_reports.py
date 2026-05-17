"""Realty-reports endpoints — market-price probe + async report creation."""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..models.realty_reports import MarketPriceCorrespondence, RealtyReportTask
from ._base import BaseMethod


class GetMarketPriceCorrespondence(BaseMethod[MarketPriceCorrespondence]):
    """Probe market-price correspondence for ``(itemId, price)``.

    Wire: ``GET /realty/v1/marketPriceCorrespondence/{itemId}/{price}``.

    Both ``itemId`` and ``price`` ride in the URL path (Avito doesn't
    accept either as a query field on this endpoint).
    """

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/realty/v1/marketPriceCorrespondence/{itemId}/{price}"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"itemId", "price"})

    itemId: int = Field(..., ge=1, description="Avito numeric item id.")
    price: int = Field(..., ge=0, description="Price to probe (integer rubles).")


class CreateRealtyReport(BaseMethod[RealtyReportTask]):
    """Kick off a realty report via ``POST /realty/v1/report/create/{itemId}``.

    Returns a task handle; the report itself is delivered out-of-band
    via Avito's task-status surface. Idempotent — same item + same
    idempotency key = same task.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/realty/v1/report/create/{itemId}"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"itemId"})
    __idempotent_mutation__: ClassVar[bool] = True

    itemId: int = Field(..., ge=1, description="Avito numeric item id.")
