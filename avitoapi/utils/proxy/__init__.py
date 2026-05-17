"""Proxy transport seam. See ``_MODULE.md``."""
from __future__ import annotations

from ._base import BaseProxyTransport, InvalidHook, NoProxyTransport, Proxy, ProxyAcquireContext
from .callback import (
    KEEP,
    CallbackProxyTransport,
    CallbackResult,
    ProxyCallback,
    ProxyContext,
)
from .parser import ProxyLike, parse_proxy, parse_proxy_list
from .rotating import (
    ListProxyTransport,
    ProxyHealth,
    RotatingProxyTransportFactory,
    RotationStrategy,
)
from .validator import ProxyCheckResult, ProxyValidator

__all__ = [
    "KEEP",
    "BaseProxyTransport",
    "CallbackProxyTransport",
    "CallbackResult",
    "InvalidHook",
    "ListProxyTransport",
    "NoProxyTransport",
    "Proxy",
    "ProxyAcquireContext",
    "ProxyCallback",
    "ProxyCheckResult",
    "ProxyContext",
    "ProxyHealth",
    "ProxyLike",
    "ProxyValidator",
    "RotatingProxyTransportFactory",
    "RotationStrategy",
    "parse_proxy",
    "parse_proxy_list",
]
