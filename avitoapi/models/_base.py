"""``BoundModel`` — Pydantic base for response DTOs carrying a client reference."""

from __future__ import annotations

from typing import Any, Self

from pydantic import BaseModel, ConfigDict, PrivateAttr

from ..exceptions import ModelNotBoundError


class BoundModel(BaseModel):
    """Pydantic v2 base for response DTOs that can fire follow-up requests.

    The session funnel calls ``.as_(client)`` on every decoded response so any
    bound methods (``order.cancel()``, ``message.reply()``) work. Hand-built models
    have no client and raise :class:`ModelNotBoundError` when those methods fire.
    """

    model_config = ConfigDict(populate_by_name=True, strict=True)

    _client: Any = PrivateAttr(default=None)

    def as_(self, client: Any) -> Self:
        """Attach a client and return ``self`` for fluent chaining.

        Recursively binds nested :class:`BoundModel` children (including inside
        ``list`` and ``dict`` containers) so chains like
        ``order.payment.refund()`` work without extra plumbing.
        """

        self._client = client
        for name in type(self).model_fields:
            value = getattr(self, name, None)
            _bind_recursive(value, client)
        return self

    def _require_client(self) -> Any:
        if self._client is None:
            raise ModelNotBoundError(
                f"{type(self).__name__} has no client bound. Build it via a Client "
                "method, or call .as_(client) before invoking bound methods.",
            )
        return self._client


def _bind_recursive(value: Any, client: Any) -> None:
    if isinstance(value, BoundModel):
        value.as_(client)
    elif isinstance(value, list):
        for item in value:
            _bind_recursive(item, client)
    elif isinstance(value, dict):
        for item in value.values():
            _bind_recursive(item, client)
