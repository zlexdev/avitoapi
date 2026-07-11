"""``BaseMethod[T]`` — aiogram-style typed endpoint declaration."""

from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Self, TypeVar, get_args

from pydantic import BaseModel, ConfigDict, PrivateAttr

from ..exceptions import MethodDeclarationError, MethodNotBoundError
from ..protocol.base import Protocol
from ..protocol.rest import RestProtocol

if TYPE_CHECKING:
    from ..client import Client

T_co = TypeVar("T_co", covariant=True)


class BaseMethod(BaseModel, Generic[T_co]):
    """Aiogram-style typed endpoint. Awaiting executes through the bound client.

    Subclasses fix wire intent via class-vars; the actual encoding is delegated
    to ``__protocol__``. The default :class:`RestProtocol` honours:

    * ``__http_method__`` — ``"GET" | "POST" | "PUT" | "PATCH" | "DELETE" | "HEAD"``.
    * ``__endpoint__`` — path template, may contain ``{name}`` placeholders; the
      protocol fills each placeholder from the field of the same name.
    * ``__idempotent_mutation__`` — auto-inject ``Idempotency-Key`` for retries.
    * ``__retry_safe__`` — mark a non-GET method safe to retry.
    * ``__multipart__`` / ``__binary_response__`` — non-JSON wire shape.

    Universal class-vars (any protocol):

    * ``__host__`` — logical host key (default ``"www"``).
    * ``__returning__`` — Pydantic class validated against the response.
    * ``__protocol__`` — protocol class (default :class:`RestProtocol`).
    * ``__breaker_path__`` — circuit-breaker scope (default = ``__endpoint__``).
    """

    model_config = ConfigDict(strict=True, populate_by_name=True)

    __host__: ClassVar[str] = "www"
    __returning__: ClassVar[type[BaseModel] | None] = None
    __protocol__: ClassVar[type[Protocol]] = RestProtocol
    __breaker_path__: ClassVar[str | None] = None

    __http_method__: ClassVar[str | None] = None
    __endpoint__: ClassVar[str | None] = None
    __idempotent_mutation__: ClassVar[bool] = False
    __retry_safe__: ClassVar[bool] = False
    __multipart__: ClassVar[bool] = False
    __binary_response__: ClassVar[bool] = False

    _client: Client | None = PrivateAttr(default=None)

    def as_(self, client: Client) -> Self:
        """Attach a client and return ``self``. Idempotent; re-binding overwrites."""

        self._client = client
        return self

    async def emit(self, client: Client) -> T_co:
        """Execute through the session funnel and return the typed response."""

        return await client.session.make_request(client, self)  # type: ignore[return-value]

    def __await__(self) -> Generator[object, None, T_co]:
        # coroutine protocol: yield type is opaque (event-loop internal), kept as object
        if self._client is None:
            raise MethodNotBoundError(
                f"{type(self).__name__} awaited without a client bound. Use "
                "`await client(method)` or `await method.as_(client)`.",
            )
        return self.emit(self._client).__await__()

    def __init_subclass__(cls, **kwargs: Any) -> None:  # typed-Any: __init_subclass__ standard signature
        super().__init_subclass__(**kwargs)
        cls.__protocol__.validate_subclass(cls)
        if "__path__" in cls.__dict__:
            raise MethodDeclarationError(
                f"{cls.__name__}: use __endpoint__, not __path__ "
                "(Python reserves __path__ for package paths).",
            )
        cls.__returning__ = cls._resolve_returning()

    @classmethod
    def _resolve_returning(cls) -> type[BaseModel] | None:
        from_generic: type[BaseModel] | None = None
        for base in getattr(cls, "__orig_bases__", ()):
            args = get_args(base)
            if args and isinstance(args[0], type) and issubclass(args[0], BaseModel):
                from_generic = args[0]
                break
        if from_generic is None:
            for parent in cls.__mro__[1:]:
                metadata = getattr(parent, "__pydantic_generic_metadata__", None)
                if not metadata:
                    continue
                args = metadata.get("args") or ()
                if args and isinstance(args[0], type) and issubclass(args[0], BaseModel):
                    from_generic = args[0]
                    break

        explicit = cls.__dict__.get("__returning__", None)
        if explicit is not None and from_generic is not None and explicit is not from_generic:
            raise MethodDeclarationError(
                f"{cls.__name__}: __returning__={explicit.__name__} contradicts "
                f"Generic parameter T_co={from_generic.__name__}. Pick one.",
            )
        return explicit if explicit is not None else from_generic
