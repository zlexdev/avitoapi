"""Per-domain Pydantic response DTOs. See ``_MODULE.md``."""
from __future__ import annotations

from ._base import BoundModel
from .accounts import Account
from .common import AvitoErrorBody, Currency, Money, Page

__all__ = [
    "Account",
    "AvitoErrorBody",
    "BoundModel",
    "Currency",
    "Money",
    "Page",
]
