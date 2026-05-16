"""Job domain — résumé search, detail, contacts (PII)."""
from __future__ import annotations

import json

from avitoapi.client import Client
from avitoapi.methods.job import GetResume, GetResumeContacts, SearchResumes
from avitoapi.models.common import Page
from avitoapi.models.job import Resume, ResumeContact, ResumeSearchQuery

from tests._fake_session import FakeSession


async def test_search_resumes_emits_post_with_body_fields(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(SearchResumes, "job/resumes_page.json")

    page = await client(
        SearchResumes(
            query="python",
            region="moscow",
            salary_from=200000,
            page=1,
            per_page=25,
        ),
    )

    assert isinstance(page, Page)
    assert len(page.items) == 1

    prepared = fake_session.sent[-1]
    assert prepared.http_method == "POST"
    assert prepared.url.endswith("/job/v1/resumes/search")
    body = prepared.body if isinstance(prepared.body, dict) else json.loads(prepared.body)  # type: ignore[arg-type]
    assert body["query"] == "python"
    assert body["region"] == "moscow"
    assert body["salary_from"] == 200000


async def test_search_resumes_from_query_dto_round_trips_fields() -> None:
    q = ResumeSearchQuery(query="go", region="spb", salary_from=150000, page=2, per_page=10)

    method = SearchResumes.from_query(q)

    assert method.query == "go"
    assert method.region == "spb"
    assert method.salary_from == 150000
    assert method.page == 2
    assert method.per_page == 10


async def test_get_resume_returns_typed_resume(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetResume, "job/resume.json")

    resume = await client(GetResume(resume_id="resume-42"))

    assert isinstance(resume, Resume)
    assert resume.id == "resume-42"
    assert resume.salary == 350000


async def test_get_resume_contacts_emits_post_with_idempotency_key(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetResumeContacts, "job/contacts.json")

    contact = await client(GetResumeContacts(resume_id="resume-42"))

    assert isinstance(contact, ResumeContact)
    assert contact.email == "candidate@example.com"
    prepared = fake_session.sent[-1]
    assert prepared.http_method == "POST"
    assert prepared.url.endswith("/job/v1/resumes/resume-42/contacts")
    assert "Idempotency-Key" in prepared.headers


async def test_resume_bound_get_contacts_builds_method_class(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetResume, "job/resume.json")
    fake_session.bind_fixture(GetResumeContacts, "job/contacts.json")

    resume = await client(GetResume(resume_id="resume-42"))

    contact = await resume.get_contacts()

    assert isinstance(contact, ResumeContact)
    assert contact.phone == "+79991112233"
