"""``Event`` — root of the typed Pydantic event hierarchy.

Every event is a Pydantic model with declared, typed fields — no more
``**kwargs`` bag. Subclasses optionally declare an ``event_name`` class-kwarg
to register themselves in :data:`Event.registry` (used by the router for
textual routes and by debug tooling); Pydantic forwards the kwarg to
``__init_subclass__``.

:attr:`dedup_key` is the stable idempotency key the dispatcher dedups on. The
default keys off the event name plus every scalar id-field **excluding
timestamps**, so a redelivered event (whose synthesised ``*_at`` differs)
still maps to the same key. Domain events override it where a field lives
inside a nested payload (e.g. :class:`~avitoapi.events.messenger.NewMessage`).
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field


class Event(BaseModel):
    """Base event class.

    ``extra="allow"`` keeps the webhook path working while it stuffs a raw
    ``message`` dict into :class:`NewMessage`; ``arbitrary_types_allowed``
    covers non-Pydantic field types. Declared fields remain the design — the
    permissive config is a safety net, not a licence to skip typing.
    """

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    __event_name__: ClassVar[str] = ""
    registry: ClassVar[dict[str, type[Event]]] = {}

    # Control state — not part of the data surface; excluded from dumps + dedup.
    flags: set[str] = Field(default_factory=set, exclude=True, repr=False)

    def __init_subclass__(cls, *, event_name: str = "", **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if event_name:
            cls.__event_name__ = event_name
            Event.registry[event_name] = cls
        elif not cls.__event_name__:
            cls.__event_name__ = cls.__qualname__

    @property
    def dedup_key(self) -> str:
        """Stable idempotency key — event name + scalar id-fields, timestamps excluded."""

        parts = [self.__event_name__ or type(self).__name__]
        for key, value in sorted(self.model_dump(exclude={"flags"}).items()):
            # datetime is not str/int → excluded; a redelivered event's fresh *_at
            # must not change the key.
            if isinstance(value, str | int) and not isinstance(value, bool):
                parts.append(f"{key}={value}")
        return "|".join(parts)


class RawWebhookEvent(Event, event_name="raw_webhook"):
    """Fallback event for unrecognised webhook payload types.

    Carries the raw ``kind`` string and the unparsed ``payload`` dict so
    handlers can still inspect or log the data without the dispatcher dropping it.
    """

    kind: str
    payload: dict[str, Any]
    account_id: str = ""

    @property
    def dedup_key(self) -> str:
        digest = hashlib.sha256(
            json.dumps(self.payload, sort_keys=True, default=str).encode("utf-8"),
        ).hexdigest()[:16]
        return f"raw_webhook:{self.kind}:{digest}"


__all__ = ["Event", "RawWebhookEvent"]
