"""Balance-domain events — emitted by the balance/operations poller.

``BalanceChanged`` fires on every absolute-amount delta observed between
two snapshots. ``BalanceLow`` fires once per crossing of the threshold
configured on the poller (debounced — does not re-fire while balance
stays below the line).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import model_validator

from .messenger import BaseEvent


class BalanceEvent(BaseEvent, event_name="balance"):
    """Common ancestor of every balance/billing event."""

    account_id: str


class BalanceChanged(BalanceEvent, event_name="balance.changed"):
    """The real-money balance changed (any direction)."""

    previous: Decimal
    current: Decimal
    occurred_at: datetime
    # Derived, not caller-supplied — computed from previous/current below.
    delta: Decimal = Decimal(0)

    @model_validator(mode="after")
    def _compute_delta(self) -> BalanceChanged:
        self.delta = self.current - self.previous
        return self


class BalanceToppedUp(BalanceEvent, event_name="balance.topped_up"):
    """An operation of type ``top_up`` (or equivalent) was observed."""

    amount: Decimal
    occurred_at: datetime
    operation_id: str | None = None


class BalanceLow(BalanceEvent, event_name="balance.low"):
    """The current balance crossed the configured low-watermark threshold."""

    current: Decimal
    threshold: Decimal
    occurred_at: datetime


class BonusReceived(BalanceEvent, event_name="balance.bonus_received"):
    """A bonus credit landed on the account (separate sub-balance)."""

    amount: Decimal
    occurred_at: datetime
    reason: str | None = None


__all__ = [
    "BalanceChanged",
    "BalanceEvent",
    "BalanceLow",
    "BalanceToppedUp",
    "BonusReceived",
]
