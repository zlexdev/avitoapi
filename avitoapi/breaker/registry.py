"""Per-endpoint circuit breaker registry.

Self-contained in-package implementation. Stateless: every breaker lives
inside :class:`BreakerRegistry`, keyed by ``(host, path)`` or
``(host, path, account_id)`` when ``ClientConfig.breaker_per_account`` is on.
"""

from __future__ import annotations

import asyncio
import re
import time
from enum import StrEnum
from typing import TYPE_CHECKING, Any  # typed-Any: pybreaker Breaker object has no public type

# Matches purely-numeric or UUID path segments that identify a specific resource.
# Replaced with ``{id}`` so all variants of one endpoint share a single breaker.
# Examples:  /items/123/photos  →  /items/{id}/photos
#            /users/550e8400-e29b-41d4-a716-446655440000  →  /users/{id}
_PATH_TEMPLATE_RE = re.compile(
    r"/(?:\d+|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(?=/|$)",
    re.IGNORECASE,
)

if TYPE_CHECKING:
    from ..config import ClientConfig


class CircuitOpenError(Exception):
    """Raised when an operation is attempted against an open breaker."""


class BreakerState(StrEnum):
    """Lifecycle of a single circuit breaker."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Per-endpoint circuit breaker.

    Lifecycle:
        CLOSED -> ``record_failure()`` repeated ``fail_threshold`` times -> OPEN
        OPEN -> wait ``open_seconds`` -> HALF_OPEN
        HALF_OPEN -> ``record_success()`` -> CLOSED
        HALF_OPEN -> ``record_failure()`` -> OPEN
    """

    def __init__(
        self,
        *,
        fail_threshold: int = 5,
        open_seconds: float = 30.0,
    ) -> None:
        self.fail_threshold = fail_threshold
        self.open_seconds = open_seconds
        self._state = BreakerState.CLOSED
        self._consecutive_failures = 0
        self._opened_at: float | None = None
        self._lock = asyncio.Lock()

    @property
    def state(self) -> BreakerState:
        """Current lifecycle phase (without performing the OPEN→HALF_OPEN time check)."""
        return self._state

    def is_open(self) -> bool:
        """Return ``True`` if the breaker would refuse a request right now.

        Transitions OPEN→HALF_OPEN once ``open_seconds`` have elapsed so the
        caller can attempt a probe call.
        """
        if self._state is BreakerState.OPEN and self._opened_at is not None:
            if time.monotonic() - self._opened_at >= self.open_seconds:
                self._state = BreakerState.HALF_OPEN
                return False
            return True
        return False

    async def record_success(self) -> None:
        """Reset failure counters and close the breaker."""
        async with self._lock:
            self._consecutive_failures = 0
            self._state = BreakerState.CLOSED
            self._opened_at = None

    async def record_failure(self) -> None:
        """Increment failures; open the breaker once the threshold is crossed."""
        async with self._lock:
            self._consecutive_failures += 1
            if (
                self._state is BreakerState.HALF_OPEN
                or self._consecutive_failures >= self.fail_threshold
            ):
                self._state = BreakerState.OPEN
                self._opened_at = time.monotonic()

    async def reset(self) -> None:
        """Force-close the breaker regardless of current state."""
        async with self._lock:
            self._consecutive_failures = 0
            self._state = BreakerState.CLOSED
            self._opened_at = None


class BreakerRegistry:
    """Lazy per-key registry of :class:`CircuitBreaker` instances.

    Key = ``(host, path)`` by default; ``(host, path, account_id)`` when
    :attr:`ClientConfig.breaker_per_account` is ``True``.
    """

    def __init__(self, config: ClientConfig) -> None:
        self._config = config
        self._breakers: dict[tuple[str, ...], Any] = {}
        self._lock = asyncio.Lock()

    @staticmethod
    def _normalize_path(path: str) -> str:
        """Replace numeric/UUID path segments with ``{id}`` to key by template."""
        return _PATH_TEMPLATE_RE.sub("/{id}", path)

    def _key_for(self, host: str, path: str, account_id: str | None) -> tuple[str, ...]:
        template = self._normalize_path(path)
        if self._config.breaker_per_account and account_id is not None:
            return (host, template, account_id)
        return (host, template)

    async def for_key(
        self,
        host: str,
        path: str,
        account_id: str | None = None,
    ) -> Any:
        """Return (or lazily create) the breaker for ``(host, path[, account_id])``."""
        key = self._key_for(host, path, account_id)
        async with self._lock:
            breaker = self._breakers.get(key)
            if breaker is None:
                breaker = self._build()
                self._breakers[key] = breaker
            return breaker

    def _build(self) -> Any:
        return CircuitBreaker(
            fail_threshold=self._config.breaker_fail_threshold,
            open_seconds=self._config.breaker_open_seconds,
        )

    def __len__(self) -> int:
        return len(self._breakers)
