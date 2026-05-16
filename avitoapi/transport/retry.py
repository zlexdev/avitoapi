"""Frozen :class:`RetryPolicy` with exponential backoff + jitter."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import ClientConfig

_RETRY_STATUSES: frozenset[int] = frozenset({408, 429, 500, 502, 503, 504})


@dataclass(slots=True, frozen=True)
class RetryPolicy:
    """How many times to retry, and how long to wait between attempts.

    ``initial_s`` and ``max_s`` define the exponential window. Each delay is
    ``min(initial_s * 2**attempt, max_s)`` with up to ``jitter_ratio`` random
    multiplier applied on top.
    """

    max_retries: int = 5
    initial_s: float = 0.5
    max_s: float = 30.0
    jitter_ratio: float = 0.25
    retry_statuses: frozenset[int] = _RETRY_STATUSES

    @classmethod
    def from_config(cls, config: ClientConfig) -> RetryPolicy:
        return cls(
            max_retries=config.max_retries,
            initial_s=config.backoff_initial_s,
            max_s=config.backoff_max_s,
        )

    def should_retry_status(self, status: int) -> bool:
        return status in self.retry_statuses

    def delay_for(self, attempt: int, *, retry_after_s: float | None = None) -> float:
        """Compute the next sleep. ``retry_after_s`` overrides exponential backoff when set."""

        if retry_after_s is not None:
            return max(0.0, retry_after_s)
        base = min(self.initial_s * (2 ** max(0, attempt)), self.max_s)
        jitter = base * self.jitter_ratio * (random.random() * 2 - 1)
        return max(0.0, base + jitter)
