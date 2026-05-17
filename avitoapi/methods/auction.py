"""CPA-auction bid endpoints.

Two methods. ``SetAuctionBids`` mutates and declares
``__idempotent_mutation__ = True``.
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..models.auction import AuctionBid, AuctionBidList, SetAuctionBidsResult
from ._base import BaseMethod


class GetAuctionBids(BaseMethod[AuctionBidList]):
    """Fetch current auction bids via ``GET /auction/1/bids``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/auction/1/bids"


class SetAuctionBids(BaseMethod[SetAuctionBidsResult]):
    """Replace auction bids via ``POST /auction/1/bids``.

    Body shape: a list of :class:`AuctionBid` rows. Idempotent — same
    payload + same idempotency key = same outcome.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/auction/1/bids"
    __idempotent_mutation__: ClassVar[bool] = True

    bids: list[AuctionBid] = Field(
        ...,
        min_length=1,
        description="Replacement set of auction bids (full list, not a delta).",
    )
