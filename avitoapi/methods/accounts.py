"""Account-domain endpoints."""
from __future__ import annotations

from typing import ClassVar

from ..models.accounts import Account
from ._base import BaseMethod


class GetSelf(BaseMethod[Account]):
    """Fetch the authenticated account's profile.

    Returns:
        ``Account`` DTO with the client pre-attached.

    Raises:
        UnauthorizedError: when the bearer token is missing or invalid.
        ForbiddenError: when the token has been revoked.
    """

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/core/v1/accounts/self"
