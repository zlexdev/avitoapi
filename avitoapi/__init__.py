"""avitoapi — aiogram-style async SDK over the Avito Partner API."""
from __future__ import annotations

from . import exceptions
from .client import Client
from .config import ClientConfig
from .exceptions import (
    AuthError,
    ForbiddenError,
    HTTPError,
    MethodNotBoundError,
    NotFoundError,
    RateLimitedError,
    RunawayPagination,
    SDKError,
    ServerError,
    UnauthorizedError,
    ValidationFailed,
)
from .methods._base import BaseMethod
from .methods.accounts import GetSelf
from .models.accounts import Account
from .models.balance import (
    Balance,
    BalanceBonus,
    Operation,
    OperationType,
)
from .models.common import AvitoErrorBody, Currency, Money, Page
from .models.items import Item, ItemStatus, VasService
from .pagination import IndexPaginator, TimeWindowPaginator
from .types import HealthState, HealthStatus, HostKey

__version__ = "0.1.0"

__all__ = [
    "Account",
    "AuthError",
    "AvitoErrorBody",
    "Balance",
    "BalanceBonus",
    "BaseMethod",
    "Client",
    "ClientConfig",
    "Currency",
    "ForbiddenError",
    "GetSelf",
    "HTTPError",
    "HealthState",
    "HealthStatus",
    "HostKey",
    "IndexPaginator",
    "Item",
    "ItemStatus",
    "MethodNotBoundError",
    "Money",
    "NotFoundError",
    "Operation",
    "OperationType",
    "Page",
    "RateLimitedError",
    "RunawayPagination",
    "SDKError",
    "ServerError",
    "TimeWindowPaginator",
    "UnauthorizedError",
    "ValidationFailed",
    "VasService",
    "__version__",
    "exceptions",
]
