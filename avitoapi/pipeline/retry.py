"""Retry / backoff primitives reusable by stages and outbound clients.

:class:`Backoff` describes a delay sequence; :class:`RetryPolicy`
combines a :class:`Backoff` with a max-attempt count and a tuple of
exception types that count as retryable.

Used by :class:`~avitoapi.pipeline.runner.PipelineRunner` to wrap each
stage call — transient failures don't burn the queue's
``max_attempts`` budget, only the stage's own.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar


class Backoff(ABC):
    """Compute the delay before retry attempt ``n``.

    Attempt numbers start at 1 (first retry). Implementations should be
    pure (no I/O) so the same policy is testable.
    """

    @abstractmethod
    def delay(self, attempt: int) -> float:
        """Return the delay in seconds before retrying ``attempt``."""


@dataclass(slots=True)
class ConstantBackoff(Backoff):
    """Same delay between every attempt. Optional jitter ± ``jitter_pct``."""

    delay_s: float = 1.0
    jitter_pct: float = 0.0

    def delay(self, attempt: int) -> float:  # noqa: ARG002 — attempt unused on purpose
        if self.jitter_pct <= 0:
            return self.delay_s
        spread = self.delay_s * self.jitter_pct
        return max(0.0, self.delay_s + random.uniform(-spread, spread))


@dataclass(slots=True)
class ExponentialBackoff(Backoff):
    """``base * (multiplier ** (attempt - 1))``, capped at ``max_delay``.

    With ``jitter=True`` (default), the actual delay is sampled uniformly
    from ``[delay/2, delay]`` — Decorrelated Jitter from AWS's playbook.
    Stops the thundering-herd when many retries align.
    """

    base: float = 0.5
    multiplier: float = 2.0
    max_delay: float = 30.0
    jitter: bool = True

    def delay(self, attempt: int) -> float:
        attempt = max(1, attempt)
        raw = self.base * (self.multiplier ** (attempt - 1))
        capped = min(self.max_delay, raw)
        if not self.jitter:
            return capped
        return random.uniform(capped / 2, capped)


@dataclass(slots=True)
class RetryPolicy:
    """Retry contract used by stages.

    * ``max_attempts`` — total attempts including the first. ``1`` = no retry.
    * ``backoff`` — delay sequence. Defaults to a sensible exponential.
    * ``retry_on`` — exception types that count as retryable. Anything
      else aborts the stage immediately.
    * ``give_up_on`` — exception types that bypass the retry even if
      they match ``retry_on``. Use for explicit "do not retry" signals.
    """

    max_attempts: int = 3
    backoff: Backoff = field(default_factory=ExponentialBackoff)
    retry_on: tuple[type[BaseException], ...] = (Exception,)
    give_up_on: tuple[type[BaseException], ...] = ()

    NONE: ClassVar[RetryPolicy]

    def should_retry(self, exc: BaseException, *, attempt: int) -> bool:
        """Return ``True`` when the runner should sleep and retry."""

        if attempt >= self.max_attempts:
            return False
        if self.give_up_on and isinstance(exc, self.give_up_on):
            return False
        return isinstance(exc, self.retry_on)


RetryPolicy.NONE = RetryPolicy(max_attempts=1, backoff=ConstantBackoff(0.0))


__all__ = [
    "Backoff",
    "ConstantBackoff",
    "ExponentialBackoff",
    "RetryPolicy",
]
