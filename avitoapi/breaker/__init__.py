"""Circuit breaker registry — keyed by ``(host, path, account_id)``.

Re-exports :class:`BreakerRegistry` + :class:`CircuitBreaker`. Self-contained,
no external runtime dep.
"""

from __future__ import annotations

from .registry import BreakerRegistry, BreakerState, CircuitBreaker, CircuitOpenError

__all__ = [
    "BreakerRegistry",
    "BreakerState",
    "CircuitBreaker",
    "CircuitOpenError",
]
