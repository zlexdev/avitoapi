"""Circuit breaker registry — keyed by ``(host, path, account_id)``.

Re-exports :class:`BreakerRegistry` plus the fallback :class:`CircuitBreaker`
used when the optional ``evented`` dependency is not installed.
"""
from __future__ import annotations

from .registry import BreakerRegistry, BreakerState, CircuitBreaker, CircuitOpenError

__all__ = [
    "BreakerRegistry",
    "BreakerState",
    "CircuitBreaker",
    "CircuitOpenError",
]
