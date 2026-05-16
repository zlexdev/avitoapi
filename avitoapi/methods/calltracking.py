"""Call-tracking endpoints — call metadata + audio recording fetch.

Three method-classes. The recording endpoint returns ``audio/mpeg`` raw bytes;
it sets ``__binary_response__ = True`` so :class:`RestProtocol.decode_response`
short-circuits the JSON decode path and returns ``raw.body`` (``bytes``)
directly — the awaited result is plain ``bytes``, not a Pydantic model.
"""
from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from ..models.calltracking import Call, CallList
from ._base import BaseMethod


class _BytesEnvelope(BaseModel):
    """Sentinel returning-type so :class:`BaseMethod` accepts a binary endpoint.

    The actual response decoded by :class:`RestProtocol` when
    ``__binary_response__`` is True is raw ``bytes``; this model is never
    instantiated but satisfies the import-time check that ``__returning__``
    is a BaseModel subclass.
    """

    model_config = ConfigDict(strict=True)


class GetCall(BaseMethod[Call]):
    """One call's metadata via ``GET /calltracking/v2/calls/{call_id}``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/calltracking/v2/calls/{call_id}"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"call_id"})

    call_id: str = Field(..., min_length=1)


class ListCalls(BaseMethod[CallList]):
    """Calls in a time window via ``GET /calltracking/v2/calls``.

    Avito returns a bare JSON array; we wrap it in :class:`CallList` so the
    funnel's "returning must be a BaseModel" contract holds. The envelope is
    iterable so callers can ``for call in calls`` without unwrapping.
    """

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/calltracking/v2/calls"

    date_from: datetime = Field(..., description="Window start (inclusive, UTC).")
    date_to: datetime = Field(..., description="Window end (inclusive, UTC).")


class GetCallRecording(BaseMethod[_BytesEnvelope]):  # type: ignore[type-var]
    """Recording audio via ``GET /calltracking/v2/calls/{call_id}/recording``.

    Sets ``__binary_response__ = True`` so :class:`RestProtocol.decode_response`
    returns the raw ``audio/mpeg`` bytes verbatim (no JSON decode, no model
    validation). The awaited result is ``bytes``.
    """

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/calltracking/v2/calls/{call_id}/recording"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"call_id"})
    __binary_response__: ClassVar[bool] = True

    call_id: str = Field(..., min_length=1)
