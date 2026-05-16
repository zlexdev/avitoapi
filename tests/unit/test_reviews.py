"""Reviews domain — list / info / reply / delete-reply round trips."""
from __future__ import annotations

import pytest
from avitoapi.client import Client
from avitoapi.exceptions import ModelNotBoundError
from avitoapi.methods.reviews import (
    DeleteReviewReply,
    GetReviewInfo,
    ListReviews,
    ReplyToReview,
)
from avitoapi.models.reviews import RatingInfo, ReviewList, ReviewReply

from tests._fake_session import FakeSession


async def test_list_reviews_decodes_envelope(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ListReviews, "reviews/list_reviews.json")

    reviews = await client(ListReviews(page=1, per_page=10))

    assert isinstance(reviews, ReviewList)
    assert len(reviews) == 2
    assert reviews.root[0].stars == 5
    assert reviews.root[1].reply is not None
    assert reviews.root[1].reply.message.startswith("Спасибо")


async def test_get_review_info_decodes_aggregates(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetReviewInfo, "reviews/rating_info.json")

    info = await client(GetReviewInfo())

    assert isinstance(info, RatingInfo)
    assert info.total == 128
    assert info.rating == pytest.approx(4.7)
    assert info.by_stars[5] == 94


async def test_reply_to_review_round_trip(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ReplyToReview, "reviews/reply.json")

    reply = await client(ReplyToReview(review_id=1001, message="Спасибо!"))

    assert isinstance(reply, ReviewReply)
    assert reply.review_id == 1001


async def test_review_bound_reply_to_uses_review_id(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ListReviews, "reviews/list_reviews.json")
    fake_session.bind_fixture(ReplyToReview, "reviews/reply.json")
    reviews = await client(ListReviews())
    first = reviews.root[0]

    reply = await first.reply_to("Спасибо!")

    assert isinstance(reply, ReviewReply)


async def test_review_reply_bound_delete_method() -> None:
    """A manually-constructed reply has no client; deletion raises."""

    from datetime import UTC, datetime

    reply = ReviewReply(
        id=42,
        review_id=1,
        message="x",
        created_at=datetime(2026, 5, 16, 12, 0, tzinfo=UTC),
    )

    with pytest.raises(ModelNotBoundError):
        reply.delete()


async def test_delete_review_reply_emits_delete(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.register(DeleteReviewReply, body=b"", status=204)

    result = await client(DeleteReviewReply(answer_id=5001))

    assert result is None
    prepared = fake_session.sent[-1]
    assert prepared.http_method == "DELETE"
    assert prepared.url.endswith("/ratings/v1/answers/5001")
