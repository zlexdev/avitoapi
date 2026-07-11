"""Propagation semantics: single-fire sub-routers, stop-propagation, status fallback."""

from __future__ import annotations

from datetime import UTC, datetime

from avitoapi.events._base import Event
from avitoapi.events.orders import OrderCreated, OrderStatus, OrderStatusChanged
from avitoapi.routers import CancelPropagation, EventContext, Router, SkipHandler
from avitoapi.web.avito_webhook_handler import AvitoWebhookHandler


def _order() -> OrderCreated:
    return OrderCreated(account_id="a1", order_id="o1", created_at=datetime.now(UTC))


async def _propagate(router: Router, event: Event) -> tuple[bool, EventContext]:
    ctx = EventContext(event=event)
    handled = await router.propagate(event, ctx)
    return handled, ctx


async def test_subrouter_handler_fires_exactly_once() -> None:
    """A handler on an included child must fire once, not once per merge + walk."""
    parent = Router(name="parent")
    child = Router(name="child")
    calls: list[str] = []

    @child.order_created()
    async def _h(_event: object, _ctx: object) -> None:
        calls.append("hit")

    parent.include_router(child)
    handled, _ = await _propagate(parent, _order())

    assert handled is True
    assert calls == ["hit"]


async def test_handler_registered_after_include_still_fires_once() -> None:
    """Registration order must not change fire count (old snapshot-merge bug)."""
    parent = Router(name="parent")
    child = Router(name="child")
    calls: list[str] = []

    parent.include_router(child)

    @child.order_created()
    async def _h(_event: object, _ctx: object) -> None:
        calls.append("hit")

    await _propagate(parent, _order())
    assert calls == ["hit"]


async def test_stop_propagation_halts_remaining_handlers() -> None:
    router = Router()
    order: list[str] = []

    @router.order_created()
    async def _first(_event: object, ctx: EventContext) -> None:
        order.append("first")
        ctx.stop_propagation()

    @router.order_created()
    async def _second(_event: object, _ctx: object) -> None:
        order.append("second")

    await _propagate(router, _order())
    assert order == ["first"]


async def test_cancel_propagation_stops_without_error() -> None:
    router = Router()
    child = Router()
    order: list[str] = []

    @router.order_created()
    async def _first(_event: object, _ctx: object) -> None:
        order.append("first")
        raise CancelPropagation

    @child.order_created()
    async def _child_handler(_event: object, _ctx: object) -> None:
        order.append("child")

    router.include_router(child)
    handled, ctx = await _propagate(router, _order())

    assert order == ["first"]
    assert ctx.is_stopped is True
    assert handled is True


async def test_skip_handler_yields_to_next() -> None:
    router = Router()
    order: list[str] = []

    @router.order_created()
    async def _skipped(_event: object, _ctx: object) -> None:
        order.append("skipped")
        raise SkipHandler

    @router.order_created()
    async def _runs(_event: object, _ctx: object) -> None:
        order.append("runs")

    await _propagate(router, _order())
    assert order == ["skipped", "runs"]


def test_unknown_order_status_maps_to_unknown() -> None:
    """Unknown upstream status must not be silently coerced to NEW."""
    event = AvitoWebhookHandler.parse_event(
        {"type": "order_status_changed", "value": {"order_id": "o9", "status": "quantum_superposition"}},
    )
    assert isinstance(event, OrderStatusChanged)
    assert event.current is OrderStatus.UNKNOWN
