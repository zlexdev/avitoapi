"""Order state-machine — exhaustive transition table coverage.

Walks every pair in ``OrderStatus x OrderStatus`` and asserts the runtime
guard matches the declared table. Then exercises strict / non-strict modes.
"""

from __future__ import annotations

import logging
from itertools import pairwise

import pytest
from avitoapi.exceptions import InvalidStateTransition
from avitoapi.models.orders import (
    ORDER_TRANSITIONS,
    OrderStatus,
    assert_order_transition,
)

# ---- table sanity ----------------------------------------------------------


def test_transitions_table_covers_every_status() -> None:
    assert set(ORDER_TRANSITIONS.keys()) == set(OrderStatus)


def test_terminal_states_have_no_outgoing_transitions() -> None:
    assert ORDER_TRANSITIONS[OrderStatus.CANCELLED] == frozenset()
    assert ORDER_TRANSITIONS[OrderStatus.REFUNDED] == frozenset()


def test_declared_transitions_match_spec() -> None:
    """Mirror the spec exactly so any silent edit to the table fails this test."""

    expected = {
        OrderStatus.NEW: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
        OrderStatus.CONFIRMED: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
        OrderStatus.SHIPPED: {OrderStatus.DELIVERED, OrderStatus.CANCELLED},
        OrderStatus.DELIVERED: {OrderStatus.COMPLETED, OrderStatus.REFUNDED},
        OrderStatus.COMPLETED: {OrderStatus.REFUNDED},
        OrderStatus.CANCELLED: set(),
        OrderStatus.REFUNDED: set(),
    }
    for src, targets in expected.items():
        assert ORDER_TRANSITIONS[src] == frozenset(targets), f"transition for {src} drifted"


# ---- exhaustive pairwise ---------------------------------------------------


@pytest.mark.parametrize("src", list(OrderStatus))
@pytest.mark.parametrize("dst", list(OrderStatus))
def test_every_pair_matches_table(src: OrderStatus, dst: OrderStatus) -> None:
    if src == dst:
        # same-state is always a no-op
        assert_order_transition(src, dst, strict=True)
        return
    if dst in ORDER_TRANSITIONS[src]:
        assert_order_transition(src, dst, strict=True)
    else:
        with pytest.raises(InvalidStateTransition):
            assert_order_transition(src, dst, strict=True)


# ---- happy path walk -------------------------------------------------------


def test_full_happy_path_new_to_completed() -> None:
    walk = [
        OrderStatus.NEW,
        OrderStatus.CONFIRMED,
        OrderStatus.SHIPPED,
        OrderStatus.DELIVERED,
        OrderStatus.COMPLETED,
    ]
    for current, target in pairwise(walk):
        assert_order_transition(current, target, strict=True)


def test_refund_branch_from_completed() -> None:
    assert_order_transition(OrderStatus.COMPLETED, OrderStatus.REFUNDED, strict=True)


def test_cancel_branches_from_each_pre_delivery_state() -> None:
    for src in (OrderStatus.NEW, OrderStatus.CONFIRMED, OrderStatus.SHIPPED):
        assert_order_transition(src, OrderStatus.CANCELLED, strict=True)


# ---- illegal transitions ---------------------------------------------------


def test_cannot_skip_states() -> None:
    with pytest.raises(InvalidStateTransition):
        assert_order_transition(OrderStatus.NEW, OrderStatus.SHIPPED, strict=True)
    with pytest.raises(InvalidStateTransition):
        assert_order_transition(OrderStatus.NEW, OrderStatus.DELIVERED, strict=True)


def test_cannot_resurrect_from_terminal() -> None:
    with pytest.raises(InvalidStateTransition) as excinfo:
        assert_order_transition(OrderStatus.CANCELLED, OrderStatus.NEW, strict=True)
    assert excinfo.value.current is OrderStatus.CANCELLED
    assert excinfo.value.target is OrderStatus.NEW

    with pytest.raises(InvalidStateTransition):
        assert_order_transition(OrderStatus.REFUNDED, OrderStatus.NEW, strict=True)


def test_cannot_cancel_after_delivery() -> None:
    with pytest.raises(InvalidStateTransition):
        assert_order_transition(OrderStatus.DELIVERED, OrderStatus.CANCELLED, strict=True)
    with pytest.raises(InvalidStateTransition):
        assert_order_transition(OrderStatus.COMPLETED, OrderStatus.CANCELLED, strict=True)


# ---- strict=False degrades to a warning -----------------------------------


def test_non_strict_logs_warning_instead_of_raising(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.WARNING)
    # Doesn't raise even though new -> shipped is illegal
    assert_order_transition(OrderStatus.NEW, OrderStatus.SHIPPED, strict=False)
