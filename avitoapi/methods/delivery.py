"""Delivery-sandbox domain — Avito Доставка integration (31 endpoints).

Every mutating call sets ``__idempotent_mutation__ = True`` so the protocol
auto-injects an ``Idempotency-Key`` header (cached in storage for 24h so
retries reuse the same key across restarts). Path templating drives ids out
of payloads into the endpoint string via ``__path_fields__``.

Naming convention: PascalCase from the path tail with ``V1``/``V2``
suffixes where the upstream surface is explicitly versioned.
"""
from __future__ import annotations

from typing import Any, ClassVar

from pydantic import Field

from ..models.delivery import (
    Announcement,
    AnnouncementEvent,
    AnnouncementId,
    ChangeParcelInfo,
    ConfirmationCheck,
    DeliveryTask,
    GenericDeliveryResult,
    OrderProperties,
    Parcel,
    ParcelChangeResult,
    ParcelInfo,
    ParcelTracking,
    RealAddress,
    RegisteredParcelId,
    SortingCenter,
    SortingCenterList,
    Tariff,
    TariffAreaList,
    TariffList,
    TariffTermList,
    TerminalList,
)
from ._base import BaseMethod


class CreateParcel(BaseMethod[Parcel]):
    """Create a parcel via ``POST /createParcel`` (legacy top-level surface)."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/createParcel"
    __idempotent_mutation__: ClassVar[bool] = True

    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Free-form parcel payload (Avito's schema is fluid; pass through).",
    )


class ListTariffAreas(BaseMethod[TariffAreaList]):
    """List areas for a tariff via ``POST /delivery-sandbox/tariffs/{tariff_id}/areas``.

    The endpoint is POST despite being a list — Avito uses a body for filters.
    Marked idempotent so retries reuse the same key.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/tariffs/{tariff_id}/areas"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"tariff_id"})
    __idempotent_mutation__: ClassVar[bool] = True

    tariff_id: str = Field(..., min_length=1)
    filters: dict[str, Any] = Field(default_factory=dict, description="Optional filter bag.")


class ListTariffTerms(BaseMethod[TariffTermList]):
    """List terms for a tariff via ``POST /delivery-sandbox/tariffs/{tariff_id}/terms``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/tariffs/{tariff_id}/terms"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"tariff_id"})
    __idempotent_mutation__: ClassVar[bool] = True

    tariff_id: str = Field(..., min_length=1)
    filters: dict[str, Any] = Field(default_factory=dict, description="Optional filter bag.")


class ListTariffsV2(BaseMethod[TariffList]):
    """List tariffs (v2) via ``POST /delivery-sandbox/tariffsV2``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/tariffsV2"
    __idempotent_mutation__: ClassVar[bool] = True

    filters: dict[str, Any] = Field(default_factory=dict, description="Free-form filter payload.")


class SetAreaCustomSchedule(BaseMethod[GenericDeliveryResult]):
    """Set a custom schedule for an area via ``POST /delivery-sandbox/areas/custom-schedule``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/areas/custom-schedule"
    __idempotent_mutation__: ClassVar[bool] = True

    area_id: str = Field(..., min_length=1)
    schedule: dict[str, Any] = Field(default_factory=dict, description="Schedule payload (free-form).")


class ListTariffTerminals(BaseMethod[TerminalList]):
    """List terminals for a tariff via ``POST /delivery-sandbox/tariffs/{tariff_id}/terminals``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/tariffs/{tariff_id}/terminals"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"tariff_id"})
    __idempotent_mutation__: ClassVar[bool] = True

    tariff_id: str = Field(..., min_length=1)
    filters: dict[str, Any] = Field(default_factory=dict, description="Optional filter bag.")


class GetDeliveryTask(BaseMethod[DeliveryTask]):
    """Fetch an async delivery task via ``GET /delivery-sandbox/tasks/{task_id}``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/tasks/{task_id}"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"task_id"})

    task_id: str = Field(..., min_length=1)


class CancelParcel(BaseMethod[ParcelChangeResult]):
    """Cancel a parcel via ``POST /delivery-sandbox/cancelParcel``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/cancelParcel"
    __idempotent_mutation__: ClassVar[bool] = True

    parcel_id: str = Field(..., min_length=1)
    reason: str | None = Field(default=None, description="Optional cancellation reason.")


class CheckConfirmationCode(BaseMethod[ConfirmationCheck]):
    """Validate a delivery confirmation code via ``POST /delivery-sandbox/order/checkConfirmationCode``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/order/checkConfirmationCode"
    __idempotent_mutation__: ClassVar[bool] = True

    order_id: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)


class SetOrderProperties(BaseMethod[OrderProperties]):
    """Set order properties via ``POST /delivery-sandbox/order/properties``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/order/properties"
    __idempotent_mutation__: ClassVar[bool] = True

    order_id: str = Field(..., min_length=1)
    properties: dict[str, Any] = Field(default_factory=dict, description="Property bag to set.")


class GetOrderRealAddress(BaseMethod[RealAddress]):
    """Resolve buyer real address via ``POST /delivery-sandbox/order/realAddress``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/order/realAddress"
    __idempotent_mutation__: ClassVar[bool] = True

    order_id: str = Field(..., min_length=1)


class GetOrderTracking(BaseMethod[ParcelTracking]):
    """Fetch order tracking via ``POST /delivery-sandbox/order/tracking``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/order/tracking"
    __idempotent_mutation__: ClassVar[bool] = True

    order_id: str = Field(..., min_length=1)


class ProhibitOrderAcceptance(BaseMethod[GenericDeliveryResult]):
    """Prohibit buyer acceptance via ``POST /delivery-sandbox/prohibitOrderAcceptance``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/prohibitOrderAcceptance"
    __idempotent_mutation__: ClassVar[bool] = True

    order_id: str = Field(..., min_length=1)
    reason: str | None = Field(default=None, description="Optional prohibition reason.")


class ChangeParcelResult(BaseMethod[ParcelChangeResult]):
    """Submit a parcel change result via ``POST /delivery/order/changeParcelResult``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery/order/changeParcelResult"
    __idempotent_mutation__: ClassVar[bool] = True

    parcel_id: str = Field(..., min_length=1)
    result: dict[str, Any] = Field(default_factory=dict, description="Result payload (free-form).")


class BatchChangeParcels(BaseMethod[ParcelChangeResult]):
    """Batch-change parcels via ``POST /sandbox/changeParcels``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/sandbox/changeParcels"
    __idempotent_mutation__: ClassVar[bool] = True

    parcels: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of parcel change payloads.",
    )


class CancelAnnouncement(BaseMethod[AnnouncementId]):
    """Cancel an announcement via ``POST /cancelAnnouncement`` (legacy top-level)."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/cancelAnnouncement"
    __idempotent_mutation__: ClassVar[bool] = True

    announcement_id: str = Field(..., min_length=1)


class CreateAnnouncement(BaseMethod[Announcement]):
    """Create an announcement via ``POST /createAnnouncement`` (legacy top-level)."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/createAnnouncement"
    __idempotent_mutation__: ClassVar[bool] = True

    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Free-form announcement payload.",
    )


class CreateAnnouncementV1(BaseMethod[Announcement]):
    """Create an announcement via ``POST /delivery-sandbox/announcements/create``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/announcements/create"
    __idempotent_mutation__: ClassVar[bool] = True

    payload: dict[str, Any] = Field(default_factory=dict, description="Free-form announcement payload.")


class TrackAnnouncementV1(BaseMethod[AnnouncementEvent]):
    """Track an announcement via ``POST /delivery-sandbox/announcements/track``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/announcements/track"
    __idempotent_mutation__: ClassVar[bool] = True

    announcement_id: str = Field(..., min_length=1)


class GetSortingCenter(BaseMethod[SortingCenter]):
    """Fetch a sorting center via ``GET /delivery-sandbox/sorting-center``.

    Avito surfaces a single sorting center per call; pass ``sorting_center_id``
    in the query string.
    """

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/sorting-center"

    sorting_center_id: str = Field(..., min_length=1)


class SetSortingCenterTariff(BaseMethod[Tariff]):
    """Attach a tariff to a sorting center via ``POST /delivery-sandbox/tariffs/sorting-center``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/tariffs/sorting-center"
    __idempotent_mutation__: ClassVar[bool] = True

    sorting_center_id: str = Field(..., min_length=1)
    tariff_id: str = Field(..., min_length=1)


class ListTariffSortingCenters(BaseMethod[SortingCenterList]):
    """List sorting centers for a tariff via ``POST /delivery-sandbox/tariffs/{tariff_id}/tagged-sorting-centers``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/tariffs/{tariff_id}/tagged-sorting-centers"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"tariff_id"})
    __idempotent_mutation__: ClassVar[bool] = True

    tariff_id: str = Field(..., min_length=1)
    filters: dict[str, Any] = Field(default_factory=dict, description="Optional filter bag.")


class CancelAnnouncementV1(BaseMethod[AnnouncementId]):
    """Cancel an announcement via ``POST /delivery-sandbox/v1/cancelAnnouncement``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/v1/cancelAnnouncement"
    __idempotent_mutation__: ClassVar[bool] = True

    announcement_id: str = Field(..., min_length=1)


class CancelParcelV1(BaseMethod[ParcelChangeResult]):
    """Cancel a parcel via ``POST /delivery-sandbox/v1/cancelParcel``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/v1/cancelParcel"
    __idempotent_mutation__: ClassVar[bool] = True

    parcel_id: str = Field(..., min_length=1)
    reason: str | None = Field(default=None, description="Optional cancellation reason.")


class ChangeParcelV1(BaseMethod[ParcelChangeResult]):
    """Change a parcel via ``POST /delivery-sandbox/v1/changeParcel``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/v1/changeParcel"
    __idempotent_mutation__: ClassVar[bool] = True

    parcel_id: str = Field(..., min_length=1)
    changes: dict[str, Any] = Field(default_factory=dict, description="Change payload (free-form).")


class CreateAnnouncementV1Alt(BaseMethod[Announcement]):
    """Create an announcement via ``POST /delivery-sandbox/v1/createAnnouncement``.

    Distinct from :class:`CreateAnnouncementV1` (``/announcements/create``) —
    Avito ships two v1 surfaces in the same namespace.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/v1/createAnnouncement"
    __idempotent_mutation__: ClassVar[bool] = True

    payload: dict[str, Any] = Field(default_factory=dict, description="Free-form announcement payload.")


class GetAnnouncementEventV1(BaseMethod[AnnouncementEvent]):
    """Fetch an announcement event via ``POST /delivery-sandbox/v1/getAnnouncementEvent``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/v1/getAnnouncementEvent"
    __idempotent_mutation__: ClassVar[bool] = True

    announcement_id: str = Field(..., min_length=1)
    event_id: str | None = Field(default=None, description="Optional specific event id.")


class GetChangeParcelInfoV1(BaseMethod[ChangeParcelInfo]):
    """Fetch change-parcel info via ``POST /delivery-sandbox/v1/getChangeParcelInfo``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/v1/getChangeParcelInfo"
    __idempotent_mutation__: ClassVar[bool] = True

    parcel_id: str = Field(..., min_length=1)


class GetParcelInfoV1(BaseMethod[ParcelInfo]):
    """Fetch parcel info via ``POST /delivery-sandbox/v1/getParcelInfo``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/v1/getParcelInfo"
    __idempotent_mutation__: ClassVar[bool] = True

    parcel_id: str = Field(..., min_length=1)


class GetRegisteredParcelIdV1(BaseMethod[RegisteredParcelId]):
    """Fetch the registered parcel id via ``POST /delivery-sandbox/v1/getRegisteredParcelID``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/v1/getRegisteredParcelID"
    __idempotent_mutation__: ClassVar[bool] = True

    external_id: str = Field(..., min_length=1)


class CreateParcelV2(BaseMethod[Parcel]):
    """Create a parcel via ``POST /delivery-sandbox/v2/createParcel``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/delivery-sandbox/v2/createParcel"
    __idempotent_mutation__: ClassVar[bool] = True

    payload: dict[str, Any] = Field(default_factory=dict, description="Free-form parcel payload.")
