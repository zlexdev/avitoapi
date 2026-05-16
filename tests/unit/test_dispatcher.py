"""Unit tests for ``avitoapi.dispatcher``."""
from __future__ import annotations

from importlib.util import find_spec

import pytest

_EVENTED_INSTALLED = find_spec("evented") is not None

pytestmark = pytest.mark.skipif(
    not _EVENTED_INSTALLED,
    reason="evented private dep required for dispatcher tests",
)


def test_dispatcher_class_exists() -> None:
    """Importing Dispatcher succeeds when evented is installed."""
    from avitoapi.dispatcher import Dispatcher

    assert Dispatcher is not None


def test_make_dispatcher_constructs_with_empty_accounts() -> None:
    """make_dispatcher() returns a Dispatcher with an empty account registry."""
    from avitoapi.dispatcher import make_dispatcher

    d = make_dispatcher(accounts=[])
    assert d is not None
    assert getattr(d, "accounts", None) == {}
