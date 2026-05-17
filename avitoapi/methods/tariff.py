"""Tariff endpoint — single read of the active subscription."""

from __future__ import annotations

from typing import ClassVar

from ..models.tariff import TariffInfo
from ._base import BaseMethod


class GetTariffInfo(BaseMethod[TariffInfo]):
    """Fetch the active subscription via ``GET /tariff/info/1``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/tariff/info/1"
