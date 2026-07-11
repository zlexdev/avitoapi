"""Review-domain events — emitted by the reviews poller.

A diff between two ``GET /ratings/v1/reviews`` snapshots produces a
:class:`ReviewReceived` for every new row and a :class:`ReviewAnswered`
when the seller answers a review (the answer text appears under
``answer`` in the next snapshot).
"""

from __future__ import annotations

from datetime import datetime

from .messenger import BaseEvent


class ReviewEvent(BaseEvent, event_name="reviews"):
    """Common ancestor of every review-domain event."""

    account_id: str
    review_id: str


class ReviewReceived(ReviewEvent, event_name="reviews.received"):
    """A buyer left a new review on one of the seller's items."""

    rating: int
    received_at: datetime
    item_id: int | None = None
    text: str | None = None


class ReviewAnswered(ReviewEvent, event_name="reviews.answered"):
    """The seller answered a review (or had one auto-answered)."""

    answer: str
    answered_at: datetime


__all__ = ["ReviewAnswered", "ReviewEvent", "ReviewReceived"]
