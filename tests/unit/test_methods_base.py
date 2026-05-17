"""Unit tests for ``avitoapi.methods._base.BaseMethod``.

Coverage:
- ``__init_subclass__`` rejects ``__path__`` (Python's package-path attribute).
- ``__init_subclass__`` reconciles ``__returning__`` with the ``Generic[T]`` param.
- A method declared as ``BaseMethod[X]`` without explicit ``__returning__`` auto-binds it.
- A method with both Generic and ``__returning__`` set to different types raises ``MethodDeclarationError``.
- Awaiting a bare (unbound) method raises ``MethodNotBoundError``.
- ``method.as_(client).emit(client)`` works end-to-end via the funnel.
"""

from __future__ import annotations

from typing import Any, ClassVar

import pytest
from avitoapi.exceptions import MethodDeclarationError, MethodNotBoundError
from avitoapi.methods._base import BaseMethod
from avitoapi.methods.accounts import GetSelf
from avitoapi.models.accounts import Account
from pydantic import BaseModel


class _Stub(BaseModel):
    id: int = 1


# ---- __path__ rejection ----------------------------------------------------


def test_subclass_with_path_attribute_raises_method_declaration_error() -> None:
    with pytest.raises(MethodDeclarationError):

        class _Broken(BaseMethod[_Stub]):
            __http_method__: ClassVar[str] = "GET"
            __endpoint__: ClassVar[str] = "/x"
            __path__: ClassVar[str] = "/x"  # type: ignore[misc]


# ---- generic / returning reconciliation -----------------------------------


def test_subclass_with_generic_only_auto_binds_returning() -> None:
    class _Auto(BaseMethod[_Stub]):
        __http_method__: ClassVar[str] = "GET"
        __endpoint__: ClassVar[str] = "/auto"

    assert _Auto.__returning__ is _Stub


def test_subclass_with_matching_generic_and_returning_keeps_returning() -> None:
    class _Match(BaseMethod[_Stub]):
        __http_method__: ClassVar[str] = "GET"
        __endpoint__: ClassVar[str] = "/match"
        __returning__: ClassVar[type[BaseModel]] = _Stub

    assert _Match.__returning__ is _Stub


def test_subclass_with_contradictory_generic_and_returning_raises() -> None:
    class _Other(BaseModel):
        id: int = 1

    with pytest.raises(MethodDeclarationError):

        class _Contradiction(BaseMethod[_Stub]):
            __http_method__: ClassVar[str] = "GET"
            __endpoint__: ClassVar[str] = "/contradict"
            __returning__: ClassVar[type[BaseModel]] = _Other


# ---- naked await raises ---------------------------------------------------


async def test_bare_method_await_raises_method_not_bound_error() -> None:
    method = GetSelf()

    with pytest.raises(MethodNotBoundError):
        await method


# ---- as_(client).emit(client) round-trip ----------------------------------


async def test_as_attaches_client_and_returns_self() -> None:
    method = GetSelf()
    sentinel = object()

    returned = method.as_(sentinel)

    assert returned is method
    assert method._client is sentinel


async def test_as_with_different_client_overrides_previous() -> None:
    method = GetSelf()
    first = object()
    second = object()

    method.as_(first)
    method.as_(second)

    assert method._client is second


async def test_emit_routes_through_session_make_request(
    client: Any,
    accounts_self_payload: dict[str, Any],
) -> None:
    """as_(client) + emit(client) must produce the same result as ``await client(method)``."""
    method = GetSelf().as_(client)

    result = await method.emit(client)

    assert isinstance(result, Account)
    assert result.id == accounts_self_payload["id"]


async def test_await_after_bind_works(
    client: Any,
    accounts_self_payload: dict[str, Any],
) -> None:
    method = GetSelf().as_(client)

    result = await method

    assert isinstance(result, Account)
    assert result.id == accounts_self_payload["id"]
