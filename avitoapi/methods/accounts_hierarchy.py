"""Accounts-hierarchy endpoints — multi-employee company surfaces.

Five endpoints. Four are read-only; ``LinkItems`` is the lone mutation
and declares ``__idempotent_mutation__ = True`` so retries are safe.
"""
from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..models.accounts_hierarchy import (
    AhUserStatus,
    EmployeeList,
    ItemList,
    LinkItemsResult,
    PhoneList,
)
from ._base import BaseMethod


class CheckAhUser(BaseMethod[AhUserStatus]):
    """Probe whether the auth'd user is inside an AH company.

    Wire: ``GET /checkAhUserV1``.
    """

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/checkAhUserV1"


class GetEmployees(BaseMethod[EmployeeList]):
    """List employees in the company via ``GET /getEmployeesV1``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/getEmployeesV1"


class LinkItems(BaseMethod[LinkItemsResult]):
    """Re-assign items between employees via ``POST /linkItemsV1``.

    Args:
        employee_id: Target employee receiving the items.
        item_ids: Avito numeric item ids to re-link.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/linkItemsV1"
    __idempotent_mutation__: ClassVar[bool] = True

    employee_id: int = Field(..., ge=1, description="Employee id to attach the items to.")
    item_ids: list[int] = Field(..., min_length=1, description="Items to re-link.")


class ListCompanyPhones(BaseMethod[PhoneList]):
    """List shared company phones via ``GET /listCompanyPhonesV1``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/listCompanyPhonesV1"


class ListItemsByEmployee(BaseMethod[ItemList]):
    """List items owned by an employee via ``POST /listItemsByEmployeeIdV1``.

    POST rather than GET because Avito accepts a bulk-filter body.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/listItemsByEmployeeIdV1"

    employee_id: int = Field(..., ge=1, description="Employee whose items to list.")
    limit: int = Field(default=100, ge=1, le=1000, description="Page size.")
    offset: int = Field(default=0, ge=0, description="Offset for paging.")
