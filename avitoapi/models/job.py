"""Job domain — résumé search + detail + contacts DTOs.

PII: ``ResumeContact.email`` and ``ResumeContact.phone`` must be redacted
by any structured-log binding (see ``logging.py``).
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

from ._base import BoundModel

if TYPE_CHECKING:
    from ..methods.job import GetResumeContacts


class ResumeSearchQuery(BaseModel):
    """Search payload for ``POST /job/v1/resumes/search``."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    query: str = Field(..., min_length=1, description="Full-text query string.")
    region: str | None = Field(default=None, description="Avito region slug or id.")
    salary_from: int | None = Field(
        default=None,
        ge=0,
        description="Lower salary bound (RUB); null = no filter.",
    )
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=25, ge=1, le=100)


class Resume(BoundModel):
    """One résumé summary row.

    Bound action :meth:`get_contacts` builds an awaitable method-class for the
    contacts endpoint — the only way to fetch the candidate's email/phone.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    id: str = Field(..., description="Avito résumé id (string).")
    title: str = Field(..., description="Résumé title / role.")
    salary: int | None = Field(
        default=None,
        ge=0,
        description="Salary expectation in RUB; null when the candidate omits it.",
    )
    region: str | None = Field(default=None, description="Region the candidate listed.")
    created_at: datetime = Field(..., description="Résumé creation timestamp (UTC).")

    def get_contacts(self) -> GetResumeContacts:
        """Build an awaitable contacts-fetch method-class bound to this résumé.

        Returns:
            ``GetResumeContacts`` with the client pre-attached.

        Raises:
            ModelNotBoundError: when the résumé was not produced by a Client call.
        """

        from ..methods.job import GetResumeContacts

        client = self._require_client()
        return GetResumeContacts(resume_id=self.id).as_(client)


class ResumeContact(BaseModel):
    """Candidate contact bundle — email + phone, both individually optional.

    PII surface — these fields must be masked in structured logs (see module
    docstring).
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    email: str | None = Field(default=None, description="Candidate email (PII).")
    phone: str | None = Field(default=None, description="Candidate phone (PII).")


def _resume_pii_fields() -> tuple[str, ...]:
    """Names of :class:`ResumeContact` fields that contain PII.

    Returned to the logging redactor (when it lifts the dependency). Keeping it
    as a function makes the contract testable in isolation.
    """

    return ("email", "phone")


__all__: list[str] = [
    "Resume",
    "ResumeContact",
    "ResumeSearchQuery",
    "_resume_pii_fields",
]


def _annotate_pii(_: Any = None) -> None:
    """No-op marker — kept so ``logging.py`` can ``import _annotate_pii`` later.

    Importing this symbol from a future logging-side redactor lets it pin
    the dependency without us having to ship the redactor today.
    """

    return None
