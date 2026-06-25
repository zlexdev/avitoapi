"""Unit tests for ``avitoapi.models._base.AvitoObject``.

Coverage:
- ``as_(client)`` sets ``_client`` and returns self.
- ``_require_client`` raises ``MethodNotBoundError`` when unbound.
- ``as_(client)`` recursively binds nested ``AvitoObject`` children.
- Recursive bind walks lists of ``AvitoObject``.
- Recursive bind walks dicts of ``AvitoObject`` values.
- A model with ``_client`` set returns it from ``_require_client``.
"""

from __future__ import annotations

import pytest
from avitoapi.exceptions import MethodNotBoundError
from avitoapi.models._base import AvitoObject


class _Child(AvitoObject):
    name: str


class _Parent(AvitoObject):
    name: str
    child: _Child | None = None


class _ListParent(AvitoObject):
    name: str
    children: list[_Child] = []


class _DictParent(AvitoObject):
    name: str
    children: dict[str, _Child] = {}


# ---- _require_client behaviour --------------------------------------------


def test_require_client_raises_when_client_is_none() -> None:
    model = _Child(name="x")

    with pytest.raises(MethodNotBoundError):
        model._require_client()


def test_require_client_returns_client_when_bound() -> None:
    model = _Child(name="x")
    sentinel = object()
    model.as_(sentinel)

    assert model._require_client() is sentinel


# ---- as_ fluent + identity ------------------------------------------------


def test_as_returns_self_for_fluent_chaining() -> None:
    model = _Child(name="x")
    sentinel = object()

    returned = model.as_(sentinel)

    assert returned is model


def test_as_sets_client_attribute() -> None:
    model = _Child(name="x")
    sentinel = object()
    model.as_(sentinel)

    assert model._client is sentinel


# ---- recursive bind: nested AvitoObject ------------------------------------


def test_as_recursively_binds_nested_bound_model_child() -> None:
    parent = _Parent(name="p", child=_Child(name="c"))
    sentinel = object()

    parent.as_(sentinel)

    assert parent.child is not None
    assert parent.child._client is sentinel


def test_as_with_none_child_does_not_raise() -> None:
    parent = _Parent(name="p", child=None)
    sentinel = object()

    parent.as_(sentinel)

    assert parent._client is sentinel


# ---- recursive bind: list of AvitoObject -----------------------------------


def test_as_recursively_binds_list_of_bound_models() -> None:
    parent = _ListParent(name="p", children=[_Child(name="a"), _Child(name="b")])
    sentinel = object()

    parent.as_(sentinel)

    assert all(child._client is sentinel for child in parent.children)


def test_as_with_empty_list_does_not_raise() -> None:
    parent = _ListParent(name="p", children=[])
    sentinel = object()

    parent.as_(sentinel)

    assert parent._client is sentinel


# ---- recursive bind: dict of AvitoObject -----------------------------------


def test_as_recursively_binds_dict_value_bound_models() -> None:
    parent = _DictParent(name="p", children={"a": _Child(name="a"), "b": _Child(name="b")})
    sentinel = object()

    parent.as_(sentinel)

    assert all(child._client is sentinel for child in parent.children.values())


def test_as_with_empty_dict_does_not_raise() -> None:
    parent = _DictParent(name="p", children={})
    sentinel = object()

    parent.as_(sentinel)

    assert parent._client is sentinel


# ---- recursive bind: deeply nested ----------------------------------------


class _Grandchild(AvitoObject):
    label: str


class _Middle(AvitoObject):
    grandchild: _Grandchild


class _Root(AvitoObject):
    middle: _Middle


def test_as_propagates_through_multiple_levels_of_nesting() -> None:
    root = _Root(middle=_Middle(grandchild=_Grandchild(label="x")))
    sentinel = object()

    root.as_(sentinel)

    assert root._client is sentinel
    assert root.middle._client is sentinel
    assert root.middle.grandchild._client is sentinel
