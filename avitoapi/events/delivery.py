"""Delivery / parcel lifecycle events.

Synthesised by the delivery poller from
``GET /delivery/v1/.../trackings`` snapshots. Carriers map to a small,
stable status vocabulary (`in_transit`, `delivered`, `returned`, ...) so
handlers can switch on string status without depending on a single
carrier's terminology.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from .messenger import BaseEvent


class DeliveryEvent(BaseEvent, event_name="delivery"):
    """Common ancestor of every delivery-domain event."""

    account_id: str
    parcel_id: str

    def __init__(self, *, account_id: str, parcel_id: str, **kwargs: Any) -> None:
        super().__init__()
        self.account_id = account_id
        self.parcel_id = parcel_id
        for k, v in kwargs.items():
            setattr(self, k, v)


class ParcelStatusChanged(DeliveryEvent, event_name="delivery.parcel_status_changed"):
    """A parcel transitioned to a new tracking state (in-transit, delivered, etc.)."""

    status: str
    previous: str | None
    occurred_at: datetime

    def __init__(
        self,
        *,
        account_id: str,
        parcel_id: str,
        status: str,
        occurred_at: datetime,
        previous: str | None = None,
    ) -> None:
        super().__init__(account_id=account_id, parcel_id=parcel_id)
        self.status = status
        self.previous = previous
        self.occurred_at = occurred_at


class ParcelHandedOver(DeliveryEvent, event_name="delivery.parcel_handed_over"):
    """The seller handed the parcel to the carrier (first physical scan)."""

    handed_over_at: datetime
    carrier: str | None

    def __init__(
        self,
        *,
        account_id: str,
        parcel_id: str,
        handed_over_at: datetime,
        carrier: str | None = None,
    ) -> None:
        super().__init__(account_id=account_id, parcel_id=parcel_id)
        self.handed_over_at = handed_over_at
        self.carrier = carrier


class ParcelDelivered(DeliveryEvent, event_name="delivery.parcel_delivered"):
    """Terminal happy-path: the buyer received the parcel."""

    delivered_at: datetime

    def __init__(self, *, account_id: str, parcel_id: str, delivered_at: datetime) -> None:
        super().__init__(account_id=account_id, parcel_id=parcel_id)
        self.delivered_at = delivered_at


class ParcelReturned(DeliveryEvent, event_name="delivery.parcel_returned"):
    """The parcel was returned to the seller (refund / no-show / refused)."""

    returned_at: datetime
    reason: str | None

    def __init__(
        self,
        *,
        account_id: str,
        parcel_id: str,
        returned_at: datetime,
        reason: str | None = None,
    ) -> None:
        super().__init__(account_id=account_id, parcel_id=parcel_id)
        self.returned_at = returned_at
        self.reason = reason


class AnnouncementTracked(DeliveryEvent, event_name="delivery.announcement_tracked"):
    """A delivery announcement has a new tracking event."""

    announcement_id: str
    event_code: str
    occurred_at: datetime

    def __init__(
        self,
        *,
        account_id: str,
        parcel_id: str,
        announcement_id: str,
        event_code: str,
        occurred_at: datetime,
    ) -> None:
        super().__init__(account_id=account_id, parcel_id=parcel_id)
        self.announcement_id = announcement_id
        self.event_code = event_code
        self.occurred_at = occurred_at


__all__ = [
    "AnnouncementTracked",
    "DeliveryEvent",
    "ParcelDelivered",
    "ParcelHandedOver",
    "ParcelReturned",
    "ParcelStatusChanged",
]
