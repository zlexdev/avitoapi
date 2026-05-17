"""Balance-domain events — emitted by the balance/operations poller.

``BalanceChanged`` fires on every absolute-amount delta observed between
two snapshots. ``BalanceLow`` fires once per crossing of the threshold
configured on the poller (debounced — does not re-fire while balance
stays below the line).
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from .messenger import BaseEvent


class BalanceEvent(BaseEvent, event_name="balance"):
    """Common ancestor of every balance/billing event."""

    account_id: str

    def __init__(self, *, account_id: str, **kwargs: Any) -> None:
        super().__init__()
        self.account_id = account_id
        for k, v in kwargs.items():
            setattr(self, k, v)


class BalanceChanged(BalanceEvent, event_name="balance.changed"):
    """The real-money balance changed (any direction)."""

    previous: Decimal
    current: Decimal
    delta: Decimal
    occurred_at: datetime

    def __init__(
        self,
        *,
        account_id: str,
        previous: Decimal,
        current: Decimal,
        occurred_at: datetime,
    ) -> None:
        super().__init__(account_id=account_id)
        self.previous = previous
        self.current = current
        self.delta = current - previous
        self.occurred_at = occurred_at


class BalanceToppedUp(BalanceEvent, event_name="balance.topped_up"):
    """An operation of type ``top_up`` (or equivalent) was observed."""

    amount: Decimal
    operation_id: str | None
    occurred_at: datetime

    def __init__(
        self,
        *,
        account_id: str,
        amount: Decimal,
        occurred_at: datetime,
        operation_id: str | None = None,
    ) -> None:
        super().__init__(account_id=account_id)
        self.amount = amount
        self.operation_id = operation_id
        self.occurred_at = occurred_at


class BalanceLow(BalanceEvent, event_name="balance.low"):
    """The current balance crossed the configured low-watermark threshold."""

    current: Decimal
    threshold: Decimal
    occurred_at: datetime

    def __init__(
        self,
        *,
        account_id: str,
        current: Decimal,
        threshold: Decimal,
        occurred_at: datetime,
    ) -> None:
        super().__init__(account_id=account_id)
        self.current = current
        self.threshold = threshold
        self.occurred_at = occurred_at


class BonusReceived(BalanceEvent, event_name="balance.bonus_received"):
    """A bonus credit landed on the account (separate sub-balance)."""

    amount: Decimal
    reason: str | None
    occurred_at: datetime

    def __init__(
        self,
        *,
        account_id: str,
        amount: Decimal,
        occurred_at: datetime,
        reason: str | None = None,
    ) -> None:
        super().__init__(account_id=account_id)
        self.amount = amount
        self.reason = reason
        self.occurred_at = occurred_at


__all__ = [
    "BalanceChanged",
    "BalanceEvent",
    "BalanceLow",
    "BalanceToppedUp",
    "BonusReceived",
]
