"""Reviews domain — ratings info, reviews list, reply / delete reply."""
from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..models.reviews import RatingInfo, ReviewList, ReviewReply
from ..pagination import PageMethod
from ._base import BaseMethod


class ListReviews(PageMethod[ReviewList]):
    """List reviews via ``GET /ratings/v1/reviews`` (paginated).

    ``ReviewList`` is a ``RootModel[list[Review]]`` — items live in ``.root``,
    picked up by the default extractor.
    """

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/ratings/v1/reviews"

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=25, ge=1, le=100)


class GetReviewInfo(BaseMethod[RatingInfo]):
    """Aggregate rating info via ``GET /ratings/v1/info``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/ratings/v1/info"


class ReplyToReview(BaseMethod[ReviewReply]):
    """Reply to a review via ``POST /ratings/v1/answers``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/ratings/v1/answers"
    __idempotent_mutation__: ClassVar[bool] = True

    review_id: int = Field(..., ge=1)
    message: str = Field(..., min_length=1, description="Reply text body.")


class DeleteReviewReply(BaseMethod[None]):
    """Delete a reply via ``DELETE /ratings/v1/answers/{answer_id}``.

    Returns ``None``; success implied by 2xx status.
    """

    __http_method__: ClassVar[str] = "DELETE"
    __endpoint__: ClassVar[str] = "/ratings/v1/answers/{answer_id}"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"answer_id"})

    answer_id: int = Field(..., ge=1)
