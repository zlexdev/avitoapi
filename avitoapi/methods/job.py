"""Job-domain endpoints — résumé search, detail, contacts (PII).

Three method-classes:

* :class:`SearchResumes` — full-text search with pagination.
* :class:`GetResume` — single résumé detail.
* :class:`GetResumeContacts` — PII fetch (email + phone). Marked
  idempotent so retries don't cost an extra "contact reveal" (Avito
  monetises these on some plans).
"""
from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..models.common import Page
from ..models.job import Resume, ResumeContact, ResumeSearchQuery
from ..pagination import PageMethod
from ._base import BaseMethod


class SearchResumes(PageMethod[Page[Resume]]):
    """Full-text résumé search via ``POST /job/v1/resumes/search``.

    Embeds the query payload directly on the method-class rather than nesting
    it under a ``query`` field, so :class:`RestProtocol`'s default body routing
    serialises it as the wire-shape Avito expects.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/job/v1/resumes/search"

    query: str = Field(..., min_length=1)
    region: str | None = Field(default=None)
    salary_from: int | None = Field(default=None, ge=0)
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=25, ge=1, le=100)

    @classmethod
    def from_query(cls, query: ResumeSearchQuery) -> SearchResumes:
        """Build a method-class from a :class:`ResumeSearchQuery` DTO.

        Useful when the caller already has the query as a DTO (e.g. parsed
        from an HTTP request body in a downstream service).
        """

        return cls(
            query=query.query,
            region=query.region,
            salary_from=query.salary_from,
            page=query.page,
            per_page=query.per_page,
        )


class GetResume(BaseMethod[Resume]):
    """One résumé via ``GET /job/v1/resumes/{resume_id}``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/job/v1/resumes/{resume_id}"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"resume_id"})

    resume_id: str = Field(..., min_length=1)


class GetResumeContacts(BaseMethod[ResumeContact]):
    """Candidate contacts via ``POST /job/v1/resumes/{resume_id}/contacts``.

    Returns PII (email, phone). The fields are masked in structured logs by
    the project's redactor (see ``models/job.py`` docstring for the contract).

    Marked idempotent so retries reuse the same ``Idempotency-Key`` header —
    Avito monetises "contact reveals" on some plans and a network blip should
    not result in a double charge.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/job/v1/resumes/{resume_id}/contacts"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"resume_id"})
    __idempotent_mutation__: ClassVar[bool] = True

    resume_id: str = Field(..., min_length=1)
