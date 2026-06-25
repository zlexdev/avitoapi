"""Callback-driven proxy transport.

The transport delegates *every* "what proxy should I use next?" decision
to a single user-supplied callable. The callable receives a
:class:`ProxyContext` snapshot (current proxy, request counts, last error,
last-error timestamp, total errors, ...) and returns either:

* a new :class:`Proxy` (parsed from anything :func:`parse_proxy` accepts) — the
  transport switches to it;
* the :data:`KEEP` sentinel — keep the current proxy unchanged;
* ``None`` — explicit "no proxy this time" (direct connection).

The same callable is invoked on proxy errors (failure path), so users can
implement the rotation policy in one place without subclassing.
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ...logging import get_logger
from ._base import BaseProxyTransport, InvalidHook, Proxy, ProxyAcquireContext
from .parser import parse_proxy

if TYPE_CHECKING:
    from ...exceptions import ProxyError

log = get_logger(__name__)


class _KeepSentinel:
    """Singleton sentinel — ``return KEEP`` means "don't replace the proxy"."""

    __slots__ = ()

    def __repr__(self) -> str:
        return "<KEEP>"


KEEP = _KeepSentinel()
"""Return this from a callback to keep the current proxy unchanged."""


CallbackResult = Proxy | str | dict[str, Any] | _KeepSentinel | None
ProxyCallback = Callable[["ProxyContext"], CallbackResult | Awaitable[CallbackResult]]


@dataclass(slots=True)
class ProxyContext:
    """Snapshot handed to the callback on every acquire / failure event.

    * ``reason`` — ``"acquire"`` for normal lookups, ``"error"`` when the
      previous attempt marked the proxy invalid.
    * ``current`` — proxy the funnel last used (``None`` for the first call
      or after a direct connection).
    * ``total_requests`` — count of acquire calls served by this transport.
    * ``total_errors`` — cumulative invalidations seen by this transport.
    * ``current_errors`` — invalidations recorded against ``current``.
    * ``last_error`` — most recent :class:`ProxyError` (may be ``None``).
    * ``last_error_at`` — monotonic seconds of the last failure (``0.0`` if none).
    * ``account_id`` / ``host`` — what the funnel passed to ``acquire``.
    * ``stats`` — read-only snapshot of per-proxy ``(requests, errors)``.
    """

    reason: str
    current: Proxy | None
    total_requests: int
    total_errors: int
    current_errors: int
    last_error: ProxyError | None
    last_error_at: float
    account_id: str | None
    host: str | None
    stats: dict[str, tuple[int, int]] = field(default_factory=dict)


@dataclass(slots=True)
class _ProxyStats:
    requests: int = 0
    errors: int = 0


class CallbackProxyTransport(BaseProxyTransport):
    """Proxy provider whose rotation policy lives in a user-supplied callback.

    Construction::

        transport = CallbackProxyTransport(get_proxy)

        # synchronous callback
        def get_proxy(ctx: ProxyContext) -> CallbackResult:
            if ctx.reason == "error":
                return next_proxy_from_pool()
            return KEEP

        # async callback also works
        async def get_proxy(ctx: ProxyContext) -> CallbackResult:
            return await async_pool.next()

    Optional ``initial`` proxy seeds ``ctx.current`` for the very first
    invocation (handy when the callback wants to roll only on failure).
    """

    def __init__(
        self,
        callback: ProxyCallback,
        *,
        initial: Proxy | str | dict[str, Any] | None = None,
    ) -> None:
        self._callback = callback
        self._current: Proxy | None = parse_proxy(initial) if initial is not None else None
        self._total_requests = 0
        self._total_errors = 0
        self._last_error: ProxyError | None = None
        self._last_error_at: float = 0.0
        self._per_proxy_stats: dict[str, _ProxyStats] = {}
        self._invalid_hooks: list[InvalidHook] = []

    def add_invalid_hook(self, hook: InvalidHook) -> None:
        self._invalid_hooks.append(hook)

    @property
    def current(self) -> Proxy | None:
        return self._current

    @property
    def total_requests(self) -> int:
        return self._total_requests

    @property
    def total_errors(self) -> int:
        return self._total_errors

    def acquire(
        self,
        *,
        account_id: str | None = None,
        host: str | None = None,
    ) -> ProxyAcquireContext:
        proxy = self._resolve(
            reason="acquire",
            account_id=account_id,
            host=host,
            last_error=None,
        )
        self._total_requests += 1
        if proxy is not None:
            self._stats_for(proxy).requests += 1
        return ProxyAcquireContext(proxy, on_release=self._on_release_factory(account_id, host))

    def _resolve(
        self,
        *,
        reason: str,
        account_id: str | None,
        host: str | None,
        last_error: ProxyError | None,
    ) -> Proxy | None:
        ctx = self._build_ctx(
            reason=reason, account_id=account_id, host=host, last_error=last_error
        )
        result = self._callback(ctx)
        if _is_awaitable(result):
            # User passed an async callback. We can't await here — acquire is
            # sync by contract. Close the orphan coroutine before surfacing a
            # clear error so the warning subsystem stays quiet.
            close = getattr(result, "close", None)
            if callable(close):
                close()
            raise TypeError(
                "CallbackProxyTransport requires a synchronous callback; "
                "drive async proxy lookup externally and call set_current(proxy) instead.",
            )
        if isinstance(result, _KeepSentinel):
            return self._current
        if result is None:
            self._current = None
            return None
        proxy = result if isinstance(result, Proxy) else parse_proxy(result)  # type: ignore[arg-type]  # awaitable case raises above; result is ProxyLike here
        self._current = proxy
        return proxy

    def _build_ctx(
        self,
        *,
        reason: str,
        account_id: str | None,
        host: str | None,
        last_error: ProxyError | None,
    ) -> ProxyContext:
        current_errors = 0
        if self._current is not None:
            stats = self._per_proxy_stats.get(self._key(self._current))
            current_errors = stats.errors if stats else 0
        return ProxyContext(
            reason=reason,
            current=self._current,
            total_requests=self._total_requests,
            total_errors=self._total_errors,
            current_errors=current_errors,
            last_error=last_error,
            last_error_at=self._last_error_at,
            account_id=account_id,
            host=host,
            stats={k: (v.requests, v.errors) for k, v in self._per_proxy_stats.items()},
        )

    def set_current(self, proxy: Proxy | str | dict[str, Any] | None) -> None:
        """Override the active proxy without going through the callback.

        Use this when an async rotation source resolved a proxy outside the
        transport (e.g. a polling task that warms the pool ahead of time).
        """

        self._current = parse_proxy(proxy) if proxy is not None else None

    def _on_release_factory(
        self,
        account_id: str | None,
        host: str | None,
    ) -> Callable[[Proxy, ProxyError | None], None]:
        def _on_release(proxy: Proxy, err: ProxyError | None) -> None:
            self._handle_error(proxy, err, account_id=account_id, host=host)

        return _on_release

    def _handle_error(
        self,
        proxy: Proxy,
        err: ProxyError | None,
        *,
        account_id: str | None,
        host: str | None,
    ) -> None:
        self._total_errors += 1
        self._stats_for(proxy).errors += 1
        self._last_error = err
        self._last_error_at = time.monotonic()
        for hook in self._invalid_hooks:
            try:
                hook(proxy, err)
            except Exception:  # noqa: BLE001 — hooks must not abort the loop
                log.exception("proxy.invalid_hook_failed", proxy=str(proxy.url))
        # Ask the callback for the next proxy. The result is cached so the
        # next ``acquire`` already sees it.
        self._resolve(reason="error", account_id=account_id, host=host, last_error=err)

    def _stats_for(self, proxy: Proxy) -> _ProxyStats:
        key = self._key(proxy)
        stats = self._per_proxy_stats.get(key)
        if stats is None:
            stats = _ProxyStats()
            self._per_proxy_stats[key] = stats
        return stats

    @staticmethod
    def _key(proxy: Proxy) -> str:
        return str(proxy.url)


def _is_awaitable(obj: Any) -> bool:
    return hasattr(obj, "__await__")


__all__ = [
    "KEEP",
    "CallbackProxyTransport",
    "CallbackResult",
    "ProxyCallback",
    "ProxyContext",
]
