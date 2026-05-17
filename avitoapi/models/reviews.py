"""Reviews domain — rating aggregates, individual reviews, replies."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, RootModel

from ._base import BoundModel

if TYPE_CHECKING:
    from ..methods.reviews import DeleteReviewReply, ReplyToReview


class Rating(BaseModel):
    """One bucket of the stars distribution (``value`` ∈ 1..5)."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    value: int = Field(..., ge=1, le=5, description="Stars bucket (1..5).")
    count: int = Field(..., ge=0, description="Number of reviews in this bucket.")


class RatingInfo(BaseModel):
    """Aggregate rating summary returned by ``GET /ratings/v1/info``."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    rating: float = Field(..., ge=0.0, le=5.0, description="Average rating across all reviews.")
    total: int = Field(..., ge=0, description="Total number of reviews.")
    by_stars: dict[int, int] = Field(
        default_factory=dict,
        description="Stars-bucket -> count distribution.",
    )


class ReviewReply(BoundModel):
    """Seller's reply attached to a review."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    id: int = Field(..., description="Reply id (numeric — Avito's ratings API uses ints).")
    review_id: int = Field(..., description="Parent review id.")
    message: str = Field(..., description="Reply text as published.")
    created_at: datetime = Field(..., description="Reply creation timestamp (UTC).")

    def delete(self) -> DeleteReviewReply:
        """Build a delete method-class bound to this reply."""

        from ..methods.reviews import DeleteReviewReply

        client = self._require_client()
        return DeleteReviewReply(answer_id=self.id).as_(client)


class Review(BoundModel):
    """A single review row from ``GET /ratings/v1/reviews``."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    id: int = Field(..., description="Review id (Avito numeric).")
    author: str = Field(..., description="Author display name.")
    stars: int = Field(..., ge=1, le=5, description="Stars (1..5).")
    text: str = Field(..., description="Review text body.")
    created_at: datetime = Field(..., description="Creation timestamp (UTC).")
    reply: ReviewReply | None = Field(default=None, description="Seller reply when present.")

    def reply_to(self, message: str) -> ReplyToReview:
        """Build a reply method-class bound to this review.

        Named ``reply_to`` so the verb doesn't collide with the ``reply`` data field.
        """

        from ..methods.reviews import ReplyToReview

        client = self._require_client()
        return ReplyToReview(review_id=self.id, message=message).as_(client)


class ReviewList(RootModel[list[Review]], BoundModel):
    """Top-level array envelope for paginated reviews responses.

    Inherits :class:`BoundModel` so the funnel cascades the client into each
    contained :class:`Review` (and its nested :class:`ReviewReply`).
    """

    root: list[Review] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)
