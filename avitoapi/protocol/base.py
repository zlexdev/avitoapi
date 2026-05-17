"""``Protocol`` ABC — separates wire-encoding from method-class intent."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..methods._base import BaseMethod
    from ..sessions._models import PreparedRequest, RawResponse, RequestContext


class Protocol(ABC):
    """Encodes a :class:`BaseMethod` into a :class:`PreparedRequest` and decodes the response.

    Subclasses: :class:`RestProtocol` (default), and later GraphQL / JSON-RPC. Each
    protocol owns:

    * a ``validate_subclass(cls)`` hook called by ``BaseMethod.__init_subclass__``
      to enforce its own required class-vars at import time;
    * ``build_request`` — translate the method instance into wire shape;
    * ``decode_response`` — validate the raw bytes into ``method.__returning__``;
    * ``is_idempotent`` — hint consumed by the retry layer (REST: GET/HEAD only).
    """

    @classmethod
    def validate_subclass(cls, method_cls: type[BaseMethod[Any]]) -> None:
        """Hook called from ``BaseMethod.__init_subclass__``. Default = no extra checks."""

    @abstractmethod
    async def build_request(
        self,
        method: BaseMethod[Any],
        ctx: RequestContext,
    ) -> PreparedRequest:
        """Translate ``method`` into a fully-prepared HTTP request.

        The protocol reads ``ctx.client.config`` for hosts / timeouts and
        ``method.__host__`` for the logical host key.
        """

    @abstractmethod
    def decode_response(
        self,
        method: BaseMethod[Any],
        raw: RawResponse,
    ) -> Any:
        """Validate the raw response body into ``method.__returning__`` (or None)."""

    @abstractmethod
    def is_idempotent(self, method: BaseMethod[Any]) -> bool:
        """Return ``True`` when the request may be retried without side-effect risk."""
