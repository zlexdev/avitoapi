"""Review-domain events — emitted by the reviews poller.

A diff between two ``GET /ratings/v1/reviews`` snapshots produces a
:class:`ReviewReceived` for every new row and a :class:`ReviewAnswered`
when the seller answers a review (the answer text appears under
``answer`` in the next snapshot).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from .messenger import BaseEvent


class ReviewEvent(BaseEvent, event_name="reviews"):
    """Common ancestor of every review-domain event."""

    account_id: str
    review_id: str

    def __init__(self, *, account_id: str, review_id: str, **kwargs: Any) -> None:
        super().__init__()
        self.account_id = account_id
        self.review_id = review_id
        for k, v in kwargs.items():
            setattr(self, k, v)


class ReviewReceived(ReviewEvent, event_name="reviews.received"):
    """A buyer left a new review on one of the seller's items."""

    rating: int
    item_id: int | None
    text: str | None
    received_at: datetime

    def __init__(
        self,
        *,
        account_id: str,
        review_id: str,
        rating: int,
        received_at: datetime,
        item_id: int | None = None,
        text: str | None = None,
    ) -> None:
        super().__init__(account_id=account_id, review_id=review_id)
        self.rating = rating
        self.item_id = item_id
        self.text = text
        self.received_at = received_at


class ReviewAnswered(ReviewEvent, event_name="reviews.answered"):
    """The seller answered a review (or had one auto-answered)."""

    answer: str
    answered_at: datetime

    def __init__(
        self,
        *,
        account_id: str,
        review_id: str,
        answer: str,
        answered_at: datetime,
    ) -> None:
        super().__init__(account_id=account_id, review_id=review_id)
        self.answer = answer
        self.answered_at = answered_at


__all__ = ["ReviewAnswered", "ReviewEvent", "ReviewReceived"]
