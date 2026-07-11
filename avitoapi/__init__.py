"""avitoapi — aiogram-style async SDK over the Avito Partner API."""

from __future__ import annotations

from . import events, exceptions, routers
from .client import Client
from .config import ClientConfig
from .exceptions import (
    AuthError,
    ForbiddenError,
    HTTPError,
    MethodNotBoundError,
    NotFoundError,
    ProxyAuthError,
    ProxyBanned,
    ProxyConnectionError,
    ProxyError,
    ProxyExhausted,
    ProxyParseError,
    ProxyTimeoutError,
    ProxyTLSError,
    RateLimitedError,
    RunawayPagination,
    SDKError,
    ServerError,
    UnauthorizedError,
    ValidationFailed,
)
from .methods._base import BaseMethod
from .models._base import AvitoObject
from .models.common import AvitoErrorBody, Currency, Money, Page, TZDatetime
from .polling import PollBatch, PollingRunner

__version__ = "0.1.0"

__all__ = [
    "AuthError",
    "AvitoErrorBody",
    "AvitoObject",
    "BaseMethod",
    "Client",
    "ClientConfig",
    "Currency",
    "ForbiddenError",
    "HTTPError",
    "MethodNotBoundError",
    "Money",
    "NotFoundError",
    "Page",
    "PollBatch",
    "PollingRunner",
    "ProxyAuthError",
    "ProxyBanned",
    "ProxyConnectionError",
    "ProxyError",
    "ProxyExhausted",
    "ProxyParseError",
    "ProxyTLSError",
    "ProxyTimeoutError",
    "RateLimitedError",
    "RunawayPagination",
    "SDKError",
    "ServerError",
    "TZDatetime",
    "UnauthorizedError",
    "ValidationFailed",
    "events",
    "exceptions",
    "routers",
]
