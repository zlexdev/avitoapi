"""Account-domain DTOs."""
from __future__ import annotations

from pydantic import EmailStr, Field, HttpUrl

from ._base import BoundModel


class Account(BoundModel):
    """Authenticated account profile returned by ``GET /core/v1/accounts/self``.

    No bound methods in W1 — order, balance, and item actions land in W2 / W5.
    """

    id: int = Field(..., description="Account numeric id (Avito user id).")
    name: str = Field(..., description="Display name.")
    email: EmailStr | None = Field(default=None, description="Primary contact email.")
    phone: str | None = Field(default=None, description="Primary contact phone.")
    profile_url: HttpUrl = Field(..., description="Public profile URL on avito.ru.")
