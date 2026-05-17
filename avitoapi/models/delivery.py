"""Delivery-sandbox domain — Avito Доставка integration DTOs.

Schema is fluid: every model uses ``ConfigDict(strict=False, extra="allow")``
so an upstream rename or extra payload key doesn't crash decoding. List
responses are wrapped in :class:`pydantic.RootModel` envelopes to satisfy the
funnel's "returning must be a ``BaseModel``" contract.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, RootModel

from ._base import BoundModel

_DELIVERY_CFG = ConfigDict(populate_by_name=True, strict=False, extra="allow")


class ParcelStatus(StrEnum):
    """Coarse parcel lifecycle states surfaced across delivery-sandbox endpoints."""

    REGISTERED = "registered"
    ACCEPTED = "accepted"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    RETURNED = "returned"
    CANCELLED = "cancelled"


class Parcel(BoundModel):
    """A parcel registered with Avito Доставка.

    Forward-compatible DTO — ``extra="allow"`` so unknown keys flow through.
    """

    model_config = _DELIVERY_CFG

    id: str | None = Field(default=None, description="Parcel id (Avito-side).")
    external_id: str | None = Field(
        default=None, description="Seller-supplied external id, when surfaced."
    )
    status: ParcelStatus | str | None = Field(
        default=None, description="Coarse status (string fallback for unknowns)."
    )
    tariff_id: str | None = Field(default=None, description="Tariff applied at registration.")
    created_at: datetime | None = Field(
        default=None, description="When the parcel was registered (UTC)."
    )
    updated_at: datetime | None = Field(default=None, description="Last server-side update (UTC).")


class ParcelTracking(BoundModel):
    """Tracking snapshot for a parcel returned by the tracking endpoints."""

    model_config = _DELIVERY_CFG

    parcel_id: str | None = Field(default=None, description="Parcel id under tracking.")
    status: ParcelStatus | str | None = Field(default=None, description="Latest status.")
    history: list[dict[str, object]] = Field(
        default_factory=list,
        description="Raw event history from the carrier; left as ``dict`` because the upstream schema is volatile.",
    )


class ParcelChangeResult(BoundModel):
    """Result envelope returned by parcel-mutation endpoints (change, batch-change)."""

    model_config = _DELIVERY_CFG

    ok: bool | None = Field(default=None, description="High-level success flag, when surfaced.")
    parcel_id: str | None = Field(default=None, description="Parcel that the change applied to.")
    details: dict[str, object] = Field(
        default_factory=dict,
        description="Free-form details bag (errors, partial updates, follow-up task ids).",
    )


class Tariff(BoundModel):
    """One tariff descriptor surfaced by ``/delivery-sandbox/tariffsV2`` and friends."""

    model_config = _DELIVERY_CFG

    id: str | None = Field(default=None, description="Tariff id.")
    name: str | None = Field(default=None, description="Human-readable tariff name.")
    carrier: str | None = Field(default=None, description="Carrier slug (cdek, post, dpd…).")


class TariffArea(BoundModel):
    """Geographic coverage entry attached to a tariff."""

    model_config = _DELIVERY_CFG

    id: str | None = Field(default=None, description="Area id, when surfaced.")
    region: str | None = Field(default=None, description="Region code or label.")
    custom_schedule: dict[str, object] | None = Field(
        default=None,
        description="Optional per-area schedule overrides.",
    )


class TariffTerm(BoundModel):
    """A single shipping term row for a tariff."""

    model_config = _DELIVERY_CFG

    id: str | None = Field(default=None, description="Term id, when surfaced.")
    min_days: int | None = Field(
        default=None, ge=0, description="Lower bound of the shipping window (days)."
    )
    max_days: int | None = Field(
        default=None, ge=0, description="Upper bound of the shipping window (days)."
    )


class Terminal(BoundModel):
    """A terminal / pickup point attached to a tariff."""

    model_config = _DELIVERY_CFG

    id: str | None = Field(default=None, description="Terminal id.")
    address: str | None = Field(default=None, description="Postal address.")
    schedule: str | None = Field(default=None, description="Free-form schedule string.")


class SortingCenter(BoundModel):
    """A sorting-center descriptor for the dedicated tariff API."""

    model_config = _DELIVERY_CFG

    id: str | None = Field(default=None, description="Sorting-center id.")
    name: str | None = Field(default=None, description="Human-readable name.")
    address: str | None = Field(default=None, description="Postal address.")


class Announcement(BoundModel):
    """An announcement (pickup request) created against a tariff."""

    model_config = _DELIVERY_CFG

    id: str | None = Field(default=None, description="Announcement id.")
    status: str | None = Field(
        default=None, description="Announcement status, free-form (status set is volatile)."
    )
    parcel_ids: list[str] = Field(
        default_factory=list, description="Parcels covered by the announcement."
    )


class AnnouncementEvent(BoundModel):
    """One event from ``/v1/getAnnouncementEvent``."""

    model_config = _DELIVERY_CFG

    type: str | None = Field(default=None, description="Event type slug.")
    occurred_at: datetime | None = Field(default=None, description="Event timestamp (UTC).")
    payload: dict[str, object] = Field(default_factory=dict, description="Raw event payload.")


class DeliveryTask(BoundModel):
    """Async task envelope returned by ``GET /delivery-sandbox/tasks/{task_id}``."""

    model_config = _DELIVERY_CFG

    id: str | None = Field(default=None, description="Task id.")
    status: str | None = Field(
        default=None, description="Task status (queued / running / succeeded / failed)."
    )
    result: dict[str, object] | None = Field(
        default=None, description="Result payload, when ready."
    )
    error: str | None = Field(default=None, description="Failure description, when present.")


class ConfirmationCheck(BoundModel):
    """Result of ``POST /delivery-sandbox/order/checkConfirmationCode``."""

    model_config = _DELIVERY_CFG

    ok: bool | None = Field(default=None, description="Whether the confirmation code matched.")
    reason: str | None = Field(default=None, description="Failure reason, when ``ok`` is False.")


class RealAddress(BoundModel):
    """Buyer-supplied delivery address resolved by the realAddress endpoint."""

    model_config = _DELIVERY_CFG

    address: str | None = Field(default=None, description="Resolved postal address string.")
    components: dict[str, object] = Field(
        default_factory=dict, description="Structured address parts."
    )


class OrderProperties(BoundModel):
    """Generic order-properties envelope shared across delivery-sandbox set/get."""

    model_config = _DELIVERY_CFG

    properties: dict[str, object] = Field(
        default_factory=dict, description="Free-form property bag."
    )


class AnnouncementId(BoundModel):
    """Result of the v1 cancel/track announcement calls when only an id flows back."""

    model_config = _DELIVERY_CFG

    id: str | None = Field(default=None, description="Announcement id touched by the call.")
    ok: bool | None = Field(default=None, description="High-level success flag.")


class ParcelInfo(BoundModel):
    """Detailed parcel info from ``POST /delivery-sandbox/v1/getParcelInfo``."""

    model_config = _DELIVERY_CFG

    parcel_id: str | None = Field(default=None, description="Parcel id.")
    status: ParcelStatus | str | None = Field(default=None, description="Latest status.")
    info: dict[str, object] = Field(default_factory=dict, description="Free-form info bag.")


class ChangeParcelInfo(BoundModel):
    """Result of ``POST /delivery-sandbox/v1/getChangeParcelInfo``."""

    model_config = _DELIVERY_CFG

    parcel_id: str | None = Field(default=None, description="Parcel id.")
    change: dict[str, object] = Field(
        default_factory=dict, description="Change descriptor returned by Avito."
    )


class RegisteredParcelId(BoundModel):
    """Result of ``POST /delivery-sandbox/v1/getRegisteredParcelID``."""

    model_config = _DELIVERY_CFG

    parcel_id: str | None = Field(default=None, description="Registered parcel id.")


class TariffList(RootModel[list[Tariff]]):
    """Root-array envelope for tariff list responses."""

    root: list[Tariff] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class TariffAreaList(RootModel[list[TariffArea]]):
    """Root-array envelope for tariff-area responses."""

    root: list[TariffArea] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class TariffTermList(RootModel[list[TariffTerm]]):
    """Root-array envelope for tariff-term responses."""

    root: list[TariffTerm] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class TerminalList(RootModel[list[Terminal]]):
    """Root-array envelope for terminal responses."""

    root: list[Terminal] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class SortingCenterList(RootModel[list[SortingCenter]]):
    """Root-array envelope for sorting-center responses."""

    root: list[SortingCenter] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class GenericDeliveryResult(BaseModel):
    """Generic ack envelope for delivery endpoints whose payload Avito has not pinned."""

    model_config = _DELIVERY_CFG

    ok: bool | None = Field(default=None, description="Generic success flag.")
    data: dict[str, object] | None = Field(default=None, description="Free-form payload.")
