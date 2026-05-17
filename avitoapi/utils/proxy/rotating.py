"""Rotating proxy transports with cumulative ban tracking."""

from __future__ import annotations

import asyncio
import random
import time
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import StrEnum

from ...exceptions import ProxyBanned, ProxyError, ProxyExhausted
from ...logging import get_logger
from ._base import BaseProxyTransport, InvalidHook, Proxy, ProxyAcquireContext
from .parser import ProxyLike, parse_proxy_list

log = get_logger(__name__)


class RotationStrategy(StrEnum):
    """How to pick the next proxy across requests."""

    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    STICKY = "sticky"  # one proxy per account_id, rotates only on failure


@dataclass(slots=True)
class ProxyHealth:
    """Per-proxy failure tally + ban state. Lives inside the transport."""

    failure_count: int = 0
    banned: bool = False
    banned_at: float = 0.0
    last_error: str | None = None
    success_count: int = 0


class ListProxyTransport(BaseProxyTransport):
    """Cycle through a static list of proxies with cumulative ban tracking.

    Construction::

        transport = ListProxyTransport(
            ["http://u:p@1.2.3.4:8080", "1.2.3.5:8080:u:p"],
            strategy=RotationStrategy.ROUND_ROBIN,
            max_failures=3,
            cooldown_s=300,
            raise_on_ban=True,
        )

    Lifecycle of one proxy:

    * Healthy → :meth:`acquire` may yield it.
    * Failed once → ``failure_count`` increments; still selectable.
    * Failed ``max_failures`` times → ``banned=True``; skipped for ``cooldown_s``;
      one :class:`ProxyBanned` is raised from the failing request when
      ``raise_on_ban=True`` (default).
    * After cooldown → reactivated, counter resets to zero.
    * If every proxy is banned at acquire time → :class:`ProxyExhausted`.
    """

    def __init__(
        self,
        proxies: Iterable[ProxyLike] | str,
        *,
        strategy: RotationStrategy = RotationStrategy.ROUND_ROBIN,
        max_failures: int = 3,
        cooldown_s: float = 300.0,
        raise_on_ban: bool = True,
        rng: random.Random | None = None,
    ) -> None:
        parsed = parse_proxy_list(proxies)
        if not parsed:
            raise ProxyExhausted("ListProxyTransport requires at least one proxy")
        self._proxies: list[Proxy] = parsed
        self._health: dict[str, ProxyHealth] = {self._key(p): ProxyHealth() for p in parsed}
        self._strategy = strategy
        self.max_failures = int(max_failures)
        self.cooldown_s = float(cooldown_s)
        self.raise_on_ban = bool(raise_on_ban)
        self._sticky: dict[str, str] = {}
        self._cursor = 0
        self._lock = asyncio.Lock()
        self._rng = rng or random.Random()
        self._invalid_hooks: list[InvalidHook] = []
        self._just_banned: dict[str, bool] = {}

    @staticmethod
    def _key(proxy: Proxy) -> str:
        return str(proxy.url)

    def add_invalid_hook(self, hook: InvalidHook) -> None:
        self._invalid_hooks.append(hook)

    def healthy(self) -> list[Proxy]:
        """Snapshot of currently-selectable proxies."""

        now = time.monotonic()
        return [p for p in self._proxies if not self._is_banned(self._key(p), now)]

    def banned(self) -> list[Proxy]:
        """Snapshot of currently-banned proxies (cooldown not elapsed)."""

        now = time.monotonic()
        return [p for p in self._proxies if self._is_banned(self._key(p), now)]

    def reset(self, proxy: Proxy | None = None) -> None:
        """Clear ban state. ``None`` resets every proxy."""

        if proxy is None:
            for h in self._health.values():
                h.failure_count = 0
                h.banned = False
                h.banned_at = 0.0
                h.last_error = None
            return
        key = self._key(proxy)
        health = self._health.get(key)
        if health is None:
            return
        health.failure_count = 0
        health.banned = False
        health.banned_at = 0.0
        health.last_error = None

    def acquire(
        self,
        *,
        account_id: str | None = None,
        host: str | None = None,
    ) -> ProxyAcquireContext:
        proxy = self._pick(account_id=account_id)
        return ProxyAcquireContext(
            proxy,
            on_release=self._on_release_factory(proxy),
        )

    def _pick(self, *, account_id: str | None) -> Proxy:
        now = time.monotonic()
        if self._strategy is RotationStrategy.STICKY and account_id is not None:
            picked = self._pick_sticky(account_id, now)
            if picked is not None:
                return picked
        candidates = [p for p in self._proxies if not self._is_banned(self._key(p), now)]
        if not candidates:
            raise ProxyExhausted(
                f"All {len(self._proxies)} proxies are banned",
            )
        if self._strategy is RotationStrategy.RANDOM:
            return self._rng.choice(candidates)
        # default → round-robin walks the original list so the cursor stays meaningful
        for _ in range(len(self._proxies)):
            picked = self._proxies[self._cursor % len(self._proxies)]
            self._cursor = (self._cursor + 1) % len(self._proxies)
            if not self._is_banned(self._key(picked), now):
                if self._strategy is RotationStrategy.STICKY and account_id is not None:
                    self._sticky[account_id] = self._key(picked)
                return picked
        raise ProxyExhausted(f"All {len(self._proxies)} proxies are banned")

    def _pick_sticky(self, account_id: str, now: float) -> Proxy | None:
        key = self._sticky.get(account_id)
        if key is None:
            return None
        if self._is_banned(key, now):
            self._sticky.pop(account_id, None)
            return None
        for proxy in self._proxies:
            if self._key(proxy) == key:
                return proxy
        self._sticky.pop(account_id, None)
        return None

    def _is_banned(self, key: str, now: float) -> bool:
        health = self._health.get(key)
        if health is None or not health.banned:
            return False
        if self.cooldown_s > 0 and now - health.banned_at >= self.cooldown_s:
            health.banned = False
            health.failure_count = 0
            health.banned_at = 0.0
            log.info("proxy.unbanned_after_cooldown", proxy=key)
            return False
        return True

    def _on_release_factory(self, proxy: Proxy | None):  # noqa: ANN202 — closure, internal
        def _on_release(p: Proxy, err: ProxyError | None) -> None:
            self._record_failure(p, err)

        return _on_release if proxy is not None else None

    def _record_failure(self, proxy: Proxy, err: ProxyError | None) -> None:
        key = self._key(proxy)
        health = self._health.get(key)
        if health is None:
            return
        health.failure_count += 1
        if err is not None:
            health.last_error = f"{type(err).__name__}: {err.detail}"
        for hook in self._invalid_hooks:
            try:
                hook(proxy, err)
            except Exception:  # noqa: BLE001 — hooks must not abort the request loop
                log.exception("proxy.invalid_hook_failed", proxy=key)

        if health.failure_count >= self.max_failures and not health.banned:
            health.banned = True
            health.banned_at = time.monotonic()
            log.warning(
                "proxy.banned",
                proxy=key,
                label=proxy.label,
                failures=health.failure_count,
                last_error=health.last_error,
            )
            if self.raise_on_ban:
                raise ProxyBanned(
                    f"Proxy {proxy.label or key} hit {health.failure_count} consecutive failures",
                    proxy_url=key,
                    failure_count=health.failure_count,
                ) from err

    def mark_success(self, proxy: Proxy) -> None:
        """Optional positive signal — callers can let us know a proxy worked."""

        health = self._health.get(self._key(proxy))
        if health is None:
            return
        health.success_count += 1
        if health.failure_count > 0 and not health.banned:
            health.failure_count = max(0, health.failure_count - 1)


@dataclass(slots=True, frozen=True)
class RotatingProxyTransportFactory:
    """Convenience factory — shorthand for the common case."""

    proxies: list[ProxyLike] = field(default_factory=list)
    strategy: RotationStrategy = RotationStrategy.ROUND_ROBIN
    max_failures: int = 3
    cooldown_s: float = 300.0
    raise_on_ban: bool = True

    def build(self) -> ListProxyTransport:
        return ListProxyTransport(
            self.proxies,
            strategy=self.strategy,
            max_failures=self.max_failures,
            cooldown_s=self.cooldown_s,
            raise_on_ban=self.raise_on_ban,
        )


__all__ = [
    "ListProxyTransport",
    "ProxyHealth",
    "RotatingProxyTransportFactory",
    "RotationStrategy",
]
