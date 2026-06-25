"""``AvitoObject`` — Pydantic base for response DTOs carrying a client reference."""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Self, TypeVar

from pydantic import BaseModel, ConfigDict, PrivateAttr, RootModel

from ..exceptions import ModelNotBoundError

if TYPE_CHECKING:
    from ..client import Client

T = TypeVar("T")


class _AvitoClientMixin:
    """Client-binding behaviour shared by object and root-model DTOs.

    The ``_client`` :data:`PrivateAttr` must be declared on each concrete Pydantic
    base (see :class:`AvitoObject` / :class:`AvitoRootObject`) — Pydantic v2 does
    **not** register a ``PrivateAttr`` declared on a plain (non-model) base, so a
    declaration here would silently never initialise and unbound models would never
    raise. This mixin therefore carries only the methods; the field lives on the
    model bases below.
    """

    _client: Client | None

    def as_(self, client: Client) -> Self:
        """Attach a client and return ``self`` for fluent chaining.

        Recursively binds nested DTO children (including inside ``list`` and ``dict``
        containers) so chains like ``order.payment.refund()`` work without plumbing.
        """
        self._client = client
        for name in type(self).model_fields:  # type: ignore[attr-defined]
            _bind_recursive(getattr(self, name, None), client)
        return self

    def _require_client(self) -> Client:
        if self._client is None:
            raise ModelNotBoundError(
                f"{type(self).__name__} has no client bound. Build it via a Client "
                "method, or call .as_(client) before invoking bound methods.",
            )
        return self._client


class AvitoObject(_AvitoClientMixin, BaseModel):
    """Pydantic v2 base for response DTOs that can fire follow-up requests.

    The session funnel calls ``.as_(client)`` on every decoded response so bound
    methods (``order.cancel()``, ``message.reply()``) work. Hand-built models have no
    client and raise :class:`ModelNotBoundError` when those methods fire.

    ``extra="allow"`` keeps forward-compat keys Avito adds over time. ``RootModel``
    list wrappers use :class:`AvitoRootObject` instead (Pydantic forbids ``extra`` on
    ``RootModel`` subclasses).
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    _client: Client | None = PrivateAttr(default=None)


class AvitoRootObject(_AvitoClientMixin, RootModel[T], Generic[T]):
    """Client-bindable ``RootModel`` base for list-wrapper DTOs (``ReviewList`` …).

    Carries the same binding contract as :class:`AvitoObject` but without ``extra``,
    which Pydantic 2.10 forbids on ``RootModel`` subclasses. ``.as_(client)`` cascades
    into the wrapped items.
    """

    _client: Client | None = PrivateAttr(default=None)


def _bind_recursive(value: object, client: Client) -> None:
    if isinstance(value, _AvitoClientMixin):
        value.as_(client)
    elif isinstance(value, list):
        for item in value:
            _bind_recursive(item, client)
    elif isinstance(value, dict):
        for item in value.values():
            _bind_recursive(item, client)
