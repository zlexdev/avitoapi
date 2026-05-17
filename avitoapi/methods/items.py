"""Items-domain endpoints — list / get / update price / VAS / archive."""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field, field_validator

from ..models.common import Page
from ..models.items import Item, ItemStatus, VasOrderResult
from ..pagination import PageMethod
from ._base import BaseMethod


class ListItems(PageMethod[Page[Item]]):
    """List own items via ``GET /core/v1/items``.

    Args:
        page: 1-based page index (Avito starts at 1, not 0).
        per_page: Items per page; capped at 100 by Avito.
        status: Optional status filter.

    Returns:
        :class:`Page` envelope of :class:`Item`.
    """

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/core/v1/items"

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=25, ge=1, le=100)
    status: ItemStatus | None = Field(default=None)

    @field_validator("per_page")
    @classmethod
    def _cap_per_page(cls, value: int) -> int:
        return min(value, 100)


class GetItem(BaseMethod[Item]):
    """Fetch a single item via ``GET /core/v1/accounts/{user_id}/items/{item_id}/``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/core/v1/accounts/{user_id}/items/{item_id}/"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id", "item_id"})

    user_id: int = Field(..., ge=1)
    item_id: int = Field(..., ge=1)


class UpdateItemPrice(BaseMethod[Item]):
    """Update an item's price via ``PUT /core/v1/accounts/{user_id}/items/{item_id}/price``.

    Idempotent mutation — auto-injects an ``Idempotency-Key`` header (see :class:`RestProtocol`).
    """

    __http_method__: ClassVar[str] = "PUT"
    __endpoint__: ClassVar[str] = "/core/v1/accounts/{user_id}/items/{item_id}/price"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id", "item_id"})
    __idempotent_mutation__: ClassVar[bool] = True

    user_id: int = Field(..., ge=1)
    item_id: int = Field(..., ge=1)
    price: int = Field(..., ge=0, description="New price in integer rubles.")


class ApplyVas(BaseMethod[VasOrderResult]):
    """Apply a single VAS (one slug) to many items via ``POST /core/v1/accounts/{user_id}/price/vas``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/core/v1/accounts/{user_id}/price/vas"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id"})
    __idempotent_mutation__: ClassVar[bool] = True

    user_id: int = Field(..., ge=1)
    item_ids: list[int] = Field(..., min_length=1)
    slug: str = Field(..., min_length=1, description="VAS service slug, e.g. ``premium``.")


class ApplyVasPackage(BaseMethod[VasOrderResult]):
    """Apply a VAS package to many items via ``POST /core/v1/accounts/{user_id}/price/vas_packages``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/core/v1/accounts/{user_id}/price/vas_packages"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id"})
    __idempotent_mutation__: ClassVar[bool] = True

    user_id: int = Field(..., ge=1)
    item_ids: list[int] = Field(..., min_length=1)
    package_id: int = Field(..., ge=1)


class ApplyVasV2(BaseMethod[VasOrderResult]):
    """Apply a VAS package to a single item via ``PUT /core/v2/accounts/{user_id}/items/{item_id}/vas_packages``."""

    __http_method__: ClassVar[str] = "PUT"
    __endpoint__: ClassVar[str] = "/core/v2/accounts/{user_id}/items/{item_id}/vas_packages"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id", "item_id"})
    __idempotent_mutation__: ClassVar[bool] = True

    user_id: int = Field(..., ge=1)
    item_id: int = Field(..., ge=1)
    package_id: int = Field(..., ge=1)


class ArchiveItem(BaseMethod[None]):
    """Archive (delete) an item via ``DELETE /core/v1/accounts/{user_id}/items/{item_id}/``.

    Returns ``None``; success implied by 2xx status.
    """

    __http_method__: ClassVar[str] = "DELETE"
    __endpoint__: ClassVar[str] = "/core/v1/accounts/{user_id}/items/{item_id}/"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id", "item_id"})

    user_id: int = Field(..., ge=1)
    item_id: int = Field(..., ge=1)
