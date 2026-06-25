"""Delivery-sandbox domain — Avito Доставка integration DTOs.

Schema is fluid: every model uses ``ConfigDict(strict=False, extra="allow")``
so an upstream rename or extra payload key doesn't crash decoding. List
responses are wrapped in :class:`pydantic.RootModel` envelopes to satisfy the
funnel's "returning must be a ``BaseModel``" contract.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, RootModel

from ..exceptions import InvalidStateTransition
from ..logging import get_logger
from ._base import AvitoObject
from .common import TZDatetime

_log = get_logger(__name__)


class ParcelStatus(StrEnum):
    """Coarse parcel lifecycle states surfaced across delivery-sandbox endpoints."""

    REGISTERED = "registered"
    ACCEPTED = "accepted"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    RETURNED = "returned"
    CANCELLED = "cancelled"


PARCEL_TRANSITIONS: dict[ParcelStatus, frozenset[ParcelStatus]] = {
    ParcelStatus.REGISTERED: frozenset({ParcelStatus.ACCEPTED, ParcelStatus.CANCELLED}),
    ParcelStatus.ACCEPTED: frozenset({ParcelStatus.IN_TRANSIT, ParcelStatus.CANCELLED}),
    ParcelStatus.IN_TRANSIT: frozenset({ParcelStatus.DELIVERED, ParcelStatus.RETURNED}),
    ParcelStatus.DELIVERED: frozenset(),
    ParcelStatus.RETURNED: frozenset(),
    ParcelStatus.CANCELLED: frozenset(),
}


def assert_parcel_transition(
    old: ParcelStatus,
    new: ParcelStatus,
    *,
    strict: bool,
) -> None:
    """Verify ``old -> new`` against :data:`PARCEL_TRANSITIONS`.

    Args:
        old: The parcel's present status.
        new: The status the caller wants to move to.
        strict: When ``True``, raise :class:`InvalidStateTransition` on an
            illegal transition. When ``False``, log a warning and let the
            mutation through.
    """
    if old == new:
        return
    allowed = PARCEL_TRANSITIONS.get(old, frozenset())
    if new in allowed:
        return
    if strict:
        raise InvalidStateTransition(
            f"Parcel cannot move {old.value} -> {new.value}; "
            f"allowed from {old.value}: {sorted(s.value for s in allowed)}",
            current=old,
            target=new,
        )
    _log.warning(
        "parcel.transition.unknown",
        current=old.value,
        target=new.value,
        allowed=sorted(s.value for s in allowed),
    )


class Parcel(AvitoObject):
    """A parcel registered with Avito Доставка.

    Forward-compatible DTO — ``extra="allow"`` so unknown keys flow through.
    """


    id: str | None = Field(default=None, description="Parcel id (Avito-side).")
    external_id: str | None = Field(
        default=None, description="Seller-supplied external id, when surfaced."
    )
    status: ParcelStatus | str | None = Field(
        default=None, description="Coarse status (string fallback for unknowns)."
    )
    tariff_id: str | None = Field(default=None, description="Tariff applied at registration.")
    created_at: TZDatetime | None = Field(
        default=None, description="When the parcel was registered (UTC)."
    )
    updated_at: TZDatetime | None = Field(default=None, description="Last server-side update (UTC).")


class ParcelTracking(AvitoObject):
    """Tracking snapshot for a parcel returned by the tracking endpoints."""


    parcel_id: str | None = Field(default=None, description="Parcel id under tracking.")
    status: ParcelStatus | str | None = Field(default=None, description="Latest status.")
    history: list[dict[str, object]] = Field(
        default_factory=list,
        description="Raw event history from the carrier; left as ``dict`` because the upstream schema is volatile.",
    )


class ParcelChangeResult(AvitoObject):
    """Result envelope returned by parcel-mutation endpoints (change, batch-change)."""


    ok: bool | None = Field(default=None, description="High-level success flag, when surfaced.")
    parcel_id: str | None = Field(default=None, description="Parcel that the change applied to.")
    details: dict[str, object] = Field(
        default_factory=dict,
        description="Free-form details bag (errors, partial updates, follow-up task ids).",
    )


class Tariff(AvitoObject):
    """One tariff descriptor surfaced by ``/delivery-sandbox/tariffsV2`` and friends."""


    id: str | None = Field(default=None, description="Tariff id.")
    name: str | None = Field(default=None, description="Human-readable tariff name.")
    carrier: str | None = Field(default=None, description="Carrier slug (cdek, post, dpd…).")


class TariffArea(AvitoObject):
    """Geographic coverage entry attached to a tariff."""


    id: str | None = Field(default=None, description="Area id, when surfaced.")
    region: str | None = Field(default=None, description="Region code or label.")
    custom_schedule: dict[str, object] | None = Field(
        default=None,
        description="Optional per-area schedule overrides.",
    )


class TariffTerm(AvitoObject):
    """A single shipping term row for a tariff."""


    id: str | None = Field(default=None, description="Term id, when surfaced.")
    min_days: int | None = Field(
        default=None, ge=0, description="Lower bound of the shipping window (days)."
    )
    max_days: int | None = Field(
        default=None, ge=0, description="Upper bound of the shipping window (days)."
    )


class Terminal(AvitoObject):
    """A terminal / pickup point attached to a tariff."""


    id: str | None = Field(default=None, description="Terminal id.")
    address: str | None = Field(default=None, description="Postal address.")
    schedule: str | None = Field(default=None, description="Free-form schedule string.")


class SortingCenter(AvitoObject):
    """A sorting-center descriptor for the dedicated tariff API."""


    id: str | None = Field(default=None, description="Sorting-center id.")
    name: str | None = Field(default=None, description="Human-readable name.")
    address: str | None = Field(default=None, description="Postal address.")


class Announcement(AvitoObject):
    """An announcement (pickup request) created against a tariff."""


    id: str | None = Field(default=None, description="Announcement id.")
    status: str | None = Field(
        default=None, description="Announcement status, free-form (status set is volatile)."
    )
    parcel_ids: list[str] = Field(
        default_factory=list, description="Parcels covered by the announcement."
    )


class AnnouncementEvent(AvitoObject):
    """One event from ``/v1/getAnnouncementEvent``."""


    type: str | None = Field(default=None, description="Event type slug.")
    occurred_at: TZDatetime | None = Field(default=None, description="Event timestamp (UTC).")
    payload: dict[str, object] = Field(default_factory=dict, description="Raw event payload.")


class DeliveryTask(AvitoObject):
    """Async task envelope returned by ``GET /delivery-sandbox/tasks/{task_id}``."""


    id: str | None = Field(default=None, description="Task id.")
    status: str | None = Field(
        default=None, description="Task status (queued / running / succeeded / failed)."
    )
    result: dict[str, object] | None = Field(
        default=None, description="Result payload, when ready."
    )
    error: str | None = Field(default=None, description="Failure description, when present.")


class ConfirmationCheck(AvitoObject):
    """Result of ``POST /delivery-sandbox/order/checkConfirmationCode``."""


    ok: bool | None = Field(default=None, description="Whether the confirmation code matched.")
    reason: str | None = Field(default=None, description="Failure reason, when ``ok`` is False.")


class RealAddress(AvitoObject):
    """Buyer-supplied delivery address resolved by the realAddress endpoint."""


    address: str | None = Field(default=None, description="Resolved postal address string.")
    components: dict[str, object] = Field(
        default_factory=dict, description="Structured address parts."
    )


class OrderProperties(AvitoObject):
    """Generic order-properties envelope shared across delivery-sandbox set/get."""


    properties: dict[str, object] = Field(
        default_factory=dict, description="Free-form property bag."
    )


class AnnouncementId(AvitoObject):
    """Result of the v1 cancel/track announcement calls when only an id flows back."""


    id: str | None = Field(default=None, description="Announcement id touched by the call.")
    ok: bool | None = Field(default=None, description="High-level success flag.")


class ParcelInfo(AvitoObject):
    """Detailed parcel info from ``POST /delivery-sandbox/v1/getParcelInfo``."""


    parcel_id: str | None = Field(default=None, description="Parcel id.")
    status: ParcelStatus | str | None = Field(default=None, description="Latest status.")
    info: dict[str, object] = Field(default_factory=dict, description="Free-form info bag.")


class ChangeParcelInfo(AvitoObject):
    """Result of ``POST /delivery-sandbox/v1/getChangeParcelInfo``."""


    parcel_id: str | None = Field(default=None, description="Parcel id.")
    change: dict[str, object] = Field(
        default_factory=dict, description="Change descriptor returned by Avito."
    )


class RegisteredParcelId(AvitoObject):
    """Result of ``POST /delivery-sandbox/v1/getRegisteredParcelID``."""


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

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    ok: bool | None = Field(default=None, description="Generic success flag.")
    data: dict[str, object] | None = Field(default=None, description="Free-form payload.")
