"""Item-listing lifecycle events — emitted by the items poller.

Diffs ``GET /core/v1/items`` snapshots: status transitions become
specialised events (`ItemPublished`, `ItemBlocked`, ...) plus a coarse
:class:`ItemStatusChanged` so handlers can subscribe at either grain.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from .messenger import BaseEvent


class ItemStatus(StrEnum):
    """Server-side item lifecycle status.

    Minimal local enum: the generated ``ItemInfoAvitoStatus`` (``avitoapi.enums.items``)
    is missing ``ARCHIVED`` — a value this module's own :class:`ItemArchived` event
    relies on — so mapping onto it would silently mis-decode archived transitions.
    """

    ACTIVE = "active"
    ARCHIVED = "archived"
    BLOCKED = "blocked"
    REMOVED = "removed"
    REJECTED = "rejected"
    OLD = "old"


class ItemEvent(BaseEvent, event_name="items"):
    """Common ancestor of every item-domain event."""

    account_id: str
    item_id: int

    def __init__(self, *, account_id: str, item_id: int, **kwargs: object) -> None:
        super().__init__()
        self.account_id = account_id
        self.item_id = item_id
        for k, v in kwargs.items():
            setattr(self, k, v)


class ItemStatusChanged(ItemEvent, event_name="items.status_changed"):
    """An item moved between two lifecycle states."""

    previous: ItemStatus
    current: ItemStatus
    occurred_at: datetime

    def __init__(
        self,
        *,
        account_id: str,
        item_id: int,
        previous: ItemStatus,
        current: ItemStatus,
        occurred_at: datetime,
    ) -> None:
        super().__init__(account_id=account_id, item_id=item_id)
        self.previous = previous
        self.current = current
        self.occurred_at = occurred_at


class ItemPublished(ItemEvent, event_name="items.published"):
    """An item became active and is now visible on the site."""

    published_at: datetime

    def __init__(self, *, account_id: str, item_id: int, published_at: datetime) -> None:
        super().__init__(account_id=account_id, item_id=item_id)
        self.published_at = published_at


class ItemBlocked(ItemEvent, event_name="items.blocked"):
    """Moderation blocked the item."""

    blocked_at: datetime
    reason: str | None

    def __init__(
        self,
        *,
        account_id: str,
        item_id: int,
        blocked_at: datetime,
        reason: str | None = None,
    ) -> None:
        super().__init__(account_id=account_id, item_id=item_id)
        self.blocked_at = blocked_at
        self.reason = reason


class ItemUnblocked(ItemEvent, event_name="items.unblocked"):
    """A previously blocked item came back to active."""

    unblocked_at: datetime

    def __init__(self, *, account_id: str, item_id: int, unblocked_at: datetime) -> None:
        super().__init__(account_id=account_id, item_id=item_id)
        self.unblocked_at = unblocked_at


class ItemSold(ItemEvent, event_name="items.sold"):
    """The seller marked the item as sold."""

    sold_at: datetime

    def __init__(self, *, account_id: str, item_id: int, sold_at: datetime) -> None:
        super().__init__(account_id=account_id, item_id=item_id)
        self.sold_at = sold_at


class ItemArchived(ItemEvent, event_name="items.archived"):
    """An item was removed from public surface and moved to archive."""

    archived_at: datetime

    def __init__(self, *, account_id: str, item_id: int, archived_at: datetime) -> None:
        super().__init__(account_id=account_id, item_id=item_id)
        self.archived_at = archived_at


__all__ = [
    "ItemArchived",
    "ItemBlocked",
    "ItemEvent",
    "ItemPublished",
    "ItemSold",
    "ItemStatusChanged",
    "ItemUnblocked",
]
