"""Proxy transport seam. ``NoProxyTransport`` is the default; rotators live in :mod:`.rotating`."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from pydantic import AnyUrl, BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from ...exceptions import ProxyError

InvalidHook = Callable[["Proxy", "ProxyError | None"], None]


class Proxy(BaseModel):
    """Single proxy endpoint. ``url`` includes scheme + auth + host + port."""

    model_config = ConfigDict(strict=True, frozen=True)

    url: AnyUrl = Field(..., description="Full proxy URL, e.g. ``http://user:pass@host:port``.")
    label: str | None = Field(default=None, description="Free-form tag for telemetry / rotation.")


class ProxyAcquireContext:
    """Async context manager returned by :meth:`BaseProxyTransport.acquire`.

    Lifecycle:

    1. Caller enters the context — yields a :class:`Proxy` or ``None``.
    2. While inside, caller may call :meth:`mark_invalid` to record a failure
       attributable to the proxy (TLS, 407, dropped connection).
    3. On ``__aexit__`` the transport's invalidation callback fires once if
       :meth:`mark_invalid` was called — that's where rotators evict / cool
       down the proxy.

    ``on_release`` is the transport's hook; it receives ``(proxy, error?)``.
    """

    __slots__ = ("_invalid", "_on_release", "_release_error", "proxy")

    def __init__(
        self,
        proxy: Proxy | None,
        *,
        on_release: Callable[[Proxy, ProxyError | None], None] | None = None,
    ) -> None:
        self.proxy: Proxy | None = proxy
        self._invalid = False
        self._release_error: ProxyError | None = None
        self._on_release = on_release

    @property
    def invalid(self) -> bool:
        return self._invalid

    def mark_invalid(self, error: ProxyError | None = None) -> None:
        """Record that this proxy attempt failed. Called from the funnel or middleware."""

        self._invalid = True
        if error is not None:
            self._release_error = error

    async def __aenter__(self) -> Proxy | None:
        return self.proxy

    async def __aexit__(self, *exc_info: Any) -> None:
        if self._invalid and self.proxy is not None and self._on_release is not None:
            self._on_release(self.proxy, self._release_error)


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

    def add_invalid_hook(self, hook: InvalidHook) -> None:
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
