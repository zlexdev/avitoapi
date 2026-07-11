"""Delivery / parcel lifecycle events.

Synthesised by the delivery poller from
``GET /delivery/v1/.../trackings`` snapshots. Carriers map to a small,
stable status vocabulary (`in_transit`, `delivered`, `returned`, ...) so
handlers can switch on string status without depending on a single
carrier's terminology.
"""

from __future__ import annotations

from datetime import datetime

from .messenger import BaseEvent


class DeliveryEvent(BaseEvent, event_name="delivery"):
    """Common ancestor of every delivery-domain event."""

    account_id: str
    parcel_id: str


class ParcelStatusChanged(DeliveryEvent, event_name="delivery.parcel_status_changed"):
    """A parcel transitioned to a new tracking state (in-transit, delivered, etc.)."""

    status: str
    occurred_at: datetime
    previous: str | None = None


class ParcelHandedOver(DeliveryEvent, event_name="delivery.parcel_handed_over"):
    """The seller handed the parcel to the carrier (first physical scan)."""

    handed_over_at: datetime
    carrier: str | None = None


class ParcelDelivered(DeliveryEvent, event_name="delivery.parcel_delivered"):
    """Terminal happy-path: the buyer received the parcel."""

    delivered_at: datetime


class ParcelReturned(DeliveryEvent, event_name="delivery.parcel_returned"):
    """The parcel was returned to the seller (refund / no-show / refused)."""

    returned_at: datetime
    reason: str | None = None


class AnnouncementTracked(DeliveryEvent, event_name="delivery.announcement_tracked"):
    """A delivery announcement has a new tracking event."""

    announcement_id: str
    event_code: str
    occurred_at: datetime


__all__ = [
    "AnnouncementTracked",
    "DeliveryEvent",
    "ParcelDelivered",
    "ParcelHandedOver",
    "ParcelReturned",
    "ParcelStatusChanged",
]
