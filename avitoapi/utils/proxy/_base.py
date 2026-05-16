"""Proxy transport seam. ``NoProxyTransport`` is the default; real rotators land in W2."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import AnyUrl, BaseModel, ConfigDict, Field


class Proxy(BaseModel):
    """Single proxy endpoint. ``url`` includes scheme + auth + host + port."""

    model_config = ConfigDict(strict=True, frozen=True)

    url: AnyUrl = Field(..., description="Full proxy URL, e.g. ``http://user:pass@host:port``.")
    label: str | None = Field(default=None, description="Free-form tag for telemetry / rotation.")


class ProxyAcquireContext:
    """Async context manager returned by :meth:`BaseProxyTransport.acquire`.

    On exit, the transport learns whether the call succeeded so rotation
    strategies can react. Use :meth:`mark_invalid` to signal that the proxy
    failed mid-request (e.g. 407, TLS handshake error).
    """

    __slots__ = ("_invalid", "proxy")

    def __init__(self, proxy: Proxy | None) -> None:
        self.proxy: Proxy | None = proxy
        self._invalid = False

    def mark_invalid(self) -> None:
        self._invalid = True

    async def __aenter__(self) -> Proxy | None:
        return self.proxy

    async def __aexit__(self, *exc_info: Any) -> None:
        return None


class BaseProxyTransport(ABC):
    """Abstract per-attempt proxy provider."""

    @abstractmethod
    def acquire(
        self,
        *,
        account_id: str | None = None,
        host: str | None = None,
    ) -> ProxyAcquireContext:
        """Return a context that yields one :class:`Proxy` (or ``None``) for this attempt."""

    def add_invalid_hook(self, hook: Any) -> None:
        """Register a callable invoked when a proxy is marked invalid. Default: no-op."""


class NoProxyTransport(BaseProxyTransport):
    """Default. Always yields ``None`` — direct connection."""

    def acquire(
        self,
        *,
        account_id: str | None = None,
        host: str | None = None,
    ) -> ProxyAcquireContext:
        return ProxyAcquireContext(proxy=None)
