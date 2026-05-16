"""Delivery / parcel lifecycle events."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from .messenger import BaseEvent


class DeliveryEvent(BaseEvent, event_name="delivery"):  # type: ignore[call-arg,misc]
    """Common ancestor of every delivery-domain event."""

    account_id: str
    parcel_id: str

    def __init__(self, *, account_id: str, parcel_id: str, **kwargs: Any) -> None:
        self.account_id = account_id
        self.parcel_id = parcel_id
        for k, v in kwargs.items():
            setattr(self, k, v)


class ParcelStatusChanged(DeliveryEvent, event_name="delivery.parcel_status_changed"):  # type: ignore[call-arg,misc]
    """A parcel transitioned to a new tracking state (in-transit, delivered, etc.)."""

    status: str
    occurred_at: datetime

    def __init__(
        self,
        *,
        account_id: str,
        parcel_id: str,
        status: str,
        occurred_at: datetime,
    ) -> None:
        super().__init__(account_id=account_id, parcel_id=parcel_id)
        self.status = status
        self.occurred_at = occurred_at


class AnnouncementTracked(DeliveryEvent, event_name="delivery.announcement_tracked"):  # type: ignore[call-arg,misc]
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
    "ParcelStatusChanged",
]
