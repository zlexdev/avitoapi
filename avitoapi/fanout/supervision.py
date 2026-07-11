"""``SupervisionPolicy`` — exponential backoff for restarting a failed source."""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SupervisionPolicy:
    """Backoff schedule for source restarts.

    ``delay_for(attempt)`` grows geometrically to ``max_delay``; ``jitter``
    spreads restarts so many sources failing at once don't reconnect in lockstep.
    ``max_restarts=None`` retries forever; a finite value gives up after that many
    consecutive failures.
    """

    base_delay: float = 1.0
    max_delay: float = 60.0
    factor: float = 2.0
    jitter: bool = True
    max_restarts: int | None = None

    def delay_for(self, attempt: int) -> float:
        """Backoff seconds for the ``attempt``-th consecutive failure (0-based)."""

        raw = self.base_delay * (self.factor**attempt)
        capped = min(self.max_delay, raw)
        if not self.jitter:
            return capped
        return random.uniform(capped / 2, capped)  # noqa: S311 — backoff jitter, not crypto

    def gives_up(self, restarts: int) -> bool:
        return self.max_restarts is not None and restarts > self.max_restarts


__all__ = ["SupervisionPolicy"]
