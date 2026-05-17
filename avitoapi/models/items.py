"""Items domain — listing DTOs, statuses, VAS service catalogue, bound actions."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from ._base import BoundModel
from .common import Money

if TYPE_CHECKING:
    from ..methods.items import ApplyVas, ArchiveItem, UpdateItemPrice


class ItemStatus(StrEnum):
    """Server-side item lifecycle returned in ``status`` field."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    BLOCKED = "blocked"
    REMOVED = "removed"
    REJECTED = "rejected"
    OLD = "old"


class VasService(StrEnum):
    """Value-added-service slugs Avito exposes on item promotion endpoints.

    Extensible — unknown slugs from the wire fall through ``ConfigDict(extra="allow")``
    on the carrying model; new public ones can be added here without breaking callers.
    """

    PREMIUM = "premium"
    HIGHLIGHT = "highlight"
    VIP = "vip"
    XL = "xl"
    TURBO = "turbo"


class ItemCategory(BaseModel):
    """Item category metadata returned inline with the item payload."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    id: int = Field(..., description="Avito numeric category id.")
    name: str = Field(..., description="Human-readable category name.")
    slug: str | None = Field(default=None, description="URL-friendly slug, when surfaced.")


class Item(BoundModel):
    """Item / listing DTO returned by ``GET /core/v1/items`` and per-item endpoints.

    Forward-compatible: extra fields from category-specific responses (Realty, Job, etc.)
    are preserved via ``ConfigDict(extra="allow")`` so callers can read raw fields
    without waiting for a model bump.

    Bound methods (`update_price`, `apply_vas`, `archive`) return awaitable
    method-class instances; the caller awaits them. Manual-constructed items
    (no client) raise :class:`ModelNotBoundError` on those actions.
    """

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    id: int = Field(..., description="Avito numeric item id.")
    status: ItemStatus = Field(..., description="Current lifecycle status.")
    title: str = Field(..., description="Listing title.")
    price: Money | None = Field(default=None, description="Current price; absent on drafts.")
    category: ItemCategory | None = Field(default=None, description="Category metadata.")
    url: HttpUrl | None = Field(default=None, description="Public URL on avito.ru.")
    created_at: datetime | None = Field(default=None, description="Creation timestamp (UTC).")
    vas: list[VasService] = Field(
        default_factory=list,
        description="Currently active VAS promotions on this item.",
    )

    def update_price(self, amount: Decimal | int) -> UpdateItemPrice:
        """Build an awaitable price-update method-class bound to this item.

        Args:
            amount: New price in integer rubles (Avito API accepts only ints).

        Returns:
            ``UpdateItemPrice`` method-class with the client pre-attached.

        Raises:
            ModelNotBoundError: when the item was not produced by a Client call.
        """
        from ..methods.items import UpdateItemPrice

        client = self._require_client()
        return UpdateItemPrice(
            user_id=_resolve_user_id(client),
            item_id=self.id,
            price=int(amount),
        ).as_(client)

    def apply_vas(self, slug: str) -> ApplyVas:
        """Build an awaitable VAS-apply method-class for this single item.

        Args:
            slug: VAS slug (use a :class:`VasService` member's ``.value`` when known).
        """
        from ..methods.items import ApplyVas

        client = self._require_client()
        return ApplyVas(
            user_id=_resolve_user_id(client),
            item_ids=[self.id],
            slug=slug,
        ).as_(client)

    def archive(self) -> ArchiveItem:
        """Build an awaitable archive method-class for this item."""
        from ..methods.items import ArchiveItem

        client = self._require_client()
        return ArchiveItem(
            user_id=_resolve_user_id(client),
            item_id=self.id,
        ).as_(client)


class VasOrderResult(BaseModel):
    """Bulk-VAS endpoint result envelope ``{success, errors[], result[]}``."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    success: bool = Field(default=False, description="True when the bulk call succeeded.")
    errors: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Per-item error rows; empty on full success.",
    )
    result: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Per-item success rows.",
    )


def _resolve_user_id(client: Any) -> int:
    user_id = getattr(client.config, "user_id", None)
    return int(user_id) if user_id is not None else 0
