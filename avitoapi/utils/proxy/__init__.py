"""Proxy transport seam. See ``_MODULE.md``."""
from __future__ import annotations

from ._base import BaseProxyTransport, NoProxyTransport, Proxy, ProxyAcquireContext

__all__ = ["BaseProxyTransport", "NoProxyTransport", "Proxy", "ProxyAcquireContext"]
