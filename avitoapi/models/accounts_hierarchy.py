"""Accounts-hierarchy domain — multi-employee company surfaces.

Avito's "accounts hierarchy" (AH) lets a company own multiple employee
sub-accounts and a single shared phone pool. The endpoints here surface
that structure read-side plus the one mutation (``LinkItems``) that
re-assigns ads between employees.

All DTOs use ``extra="allow"`` so callers can read forward-compat keys
Avito ships before this file is bumped.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, RootModel

from ._base import BoundModel


class AhUserStatus(BoundModel):
    """Result of ``GET /checkAhUserV1`` — is this user inside an AH company?"""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    is_ah_user: bool = Field(
        ...,
        alias="isAhUser",
        description="True when the user belongs to an accounts-hierarchy company.",
    )
    company_id: int | None = Field(
        default=None,
        alias="companyId",
        description="Owning company id when ``is_ah_user`` is true.",
    )
    role: str | None = Field(
        default=None,
        description="Role inside the company (owner / manager / employee / …).",
    )


class Employee(BaseModel):
    """One employee row from ``GET /getEmployeesV1``."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    id: int = Field(..., description="Employee user id (Avito numeric).")
    name: str | None = Field(default=None, description="Display name.")
    email: str | None = Field(default=None, description="Contact email.")
    role: str | None = Field(default=None, description="Role label inside the company.")


class EmployeeList(RootModel[list[Employee]]):
    """Top-level array envelope for employees responses."""

    root: list[Employee] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class CompanyPhone(BaseModel):
    """One row from ``GET /listCompanyPhonesV1`` — shared company phone slot."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    phone: str = Field(..., description="E.164 or Avito-internal phone string.")
    label: str | None = Field(default=None, description="Free-form label (sales / support / …).")
    employee_id: int | None = Field(
        default=None,
        alias="employeeId",
        description="Owning employee id when the phone is pinned to one.",
    )


class PhoneList(RootModel[list[CompanyPhone]]):
    """Top-level array envelope for company-phones responses."""

    root: list[CompanyPhone] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class EmployeeItem(BaseModel):
    """One item row returned by ``POST /listItemsByEmployeeIdV1``."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    id: int = Field(..., description="Avito numeric item id.")
    title: str | None = Field(default=None, description="Listing title.")
    employee_id: int | None = Field(
        default=None,
        alias="employeeId",
        description="Owning employee id.",
    )


class ItemList(RootModel[list[EmployeeItem]]):
    """Top-level array envelope for employee-items responses."""

    root: list[EmployeeItem] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class LinkItemsResult(BoundModel):
    """Result of ``POST /linkItemsV1`` — best-effort acknowledgement envelope."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    success: bool = Field(default=True, description="True on 2xx; Avito returns minimal body.")
    linked: int | None = Field(
        default=None,
        description="Count of items actually re-linked when surfaced.",
    )
