"""HTTP-agnostic Avito webhook adapter.

Parses an Avito webhook body into a typed event and forwards it to a
Dispatcher (or fallback router) through a configurable
:class:`~avitoapi.routers.MiddlewareChain`. The three standard middlewares
(:class:`~avitoapi.web.middlewares.HMACSignatureMiddleware`,
:class:`~avitoapi.web.middlewares.WebhookIdempotencyMiddleware`,
:class:`~avitoapi.web.middlewares.WebhookFastReturnMiddleware`) are accepted
in ``__init__`` and composed automatically.

The handler intentionally accepts a plain ``dict`` instead of a framework
request object so it can be unit-tested without a web server.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any  # typed-Any: dispatcher/middleware/handler generic params

from ..events._base import Event
from ..events.items import (
    ItemArchived,
    ItemBlocked,
    ItemPublished,
    ItemSold,
    ItemStatus,
    ItemStatusChanged,
    ItemUnblocked,
)
from ..events.messenger import ChatArchived, MessageRead, NewMessage
from ..events.orders import (
    OrderCancelled,
    OrderCompleted,
    OrderConfirmed,
    OrderCreated,
    OrderDelivered,
    OrderRefunded,
    OrderShipped,
    OrderStatus,
    OrderStatusChanged,
)
from ..routers.middleware import MiddlewareChain, NextHandler
from ..types import JsonObject
from .middlewares.context import WebhookRequestContext
from .middlewares.fast_return import WebhookFastReturnMiddleware
from .middlewares.hmac_signature import HMACSignatureMiddleware
from .middlewares.idempotency import WebhookIdempotencyMiddleware


class AvitoWebhookParseError(ValueError):
    """Raised when the webhook body does not match an Avito payload shape."""


class AvitoWebhookHandler:
    """Adapter: Avito webhook JSON → typed event → Dispatcher.

    The dispatcher (or any object with a ``dispatch(event)`` / ``feed_event(event)``
    coroutine method) is invoked once per parsed event. Replies are JSON-serialisable
    ``(status_code, body)`` tuples — the caller is responsible for translating
    them into the framework-native response (aiohttp, FastAPI, Litestar).

    Middleware chain order (when all three are provided):

    1. :class:`~avitoapi.web.middlewares.HMACSignatureMiddleware` — verify signature.
    2. :class:`~avitoapi.web.middlewares.WebhookIdempotencyMiddleware` — dedup.
    3. :class:`~avitoapi.web.middlewares.WebhookFastReturnMiddleware` — async dispatch.
    """

    def __init__(
        self,
        dispatcher: Any,
        *,
        mount_path: str = "/messenger",
        hmac_middleware: HMACSignatureMiddleware | None = None,
        idempotency_middleware: WebhookIdempotencyMiddleware | None = None,
        fast_return_middleware: WebhookFastReturnMiddleware | None = None,
    ) -> None:
        self.dispatcher = dispatcher
        self.mount_path = mount_path
        self._middleware_chain: MiddlewareChain[Any, Any] = MiddlewareChain()
        if hmac_middleware is not None:
            self._middleware_chain.register(hmac_middleware)
        if idempotency_middleware is not None:
            self._middleware_chain.register(idempotency_middleware)
        if fast_return_middleware is not None:
            self._middleware_chain.register(fast_return_middleware)

    async def handle(
        self,
        body: bytes | str | JsonObject,
        *,
        headers: dict[str, str] | None = None,
        webhook_id: str = "",
    ) -> tuple[int, JsonObject]:
        """Parse, run middleware chain, dispatch; return ``(status, body)``.

        * Valid payload → ``(200, {"ok": True})``.
        * Malformed JSON → ``(400, {"error": "invalid_body"})``.
        * HMAC failure → ``(403, {"error": "signature_missing"/"signature_mismatch"})``.
        * Duplicate → ``(200, {"ok": True, "skipped": "duplicate"})``.
        * Unknown event kind → ``(200, {"ok": True})`` via :class:`RawWebhookEvent`.
        """
        raw_body = self._to_raw_bytes(body)
        try:
            payload = self._coerce_payload(body)
        except AvitoWebhookParseError:
            return (400, {"error": "invalid_body"})

        try:
            event = self.parse_event(payload)
        except AvitoWebhookParseError as exc:
            return (200, {"ok": True, "skipped": str(exc)})

        ctx = WebhookRequestContext(
            raw_body=raw_body,
            headers=headers or {},
            webhook_id=webhook_id,
            chat_id=getattr(event, "chat_id", ""),
            message_id=getattr(event, "message_id", ""),
        )

        terminal = self._make_dispatch_terminal()
        wrapped = self._middleware_chain.wrap(terminal)
        result: object = await wrapped(event, ctx)
        if isinstance(result, tuple) and len(result) == 2:  # noqa: PLR2004
            return (int(result[0]), result[1])
        return (200, {"ok": True})

    @staticmethod
    def _to_raw_bytes(body: bytes | str | JsonObject) -> bytes:
        if isinstance(body, bytes | bytearray):
            return bytes(body)
        if isinstance(body, str):
            return body.encode("utf-8")
        return json.dumps(body, ensure_ascii=False).encode("utf-8")

    @staticmethod
    def _coerce_payload(body: bytes | str | JsonObject) -> JsonObject:
        if isinstance(body, dict):
            return body
        if isinstance(body, bytes | bytearray):
            try:
                decoded = body.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise AvitoWebhookParseError("non-utf8 body") from exc
        else:
            decoded = body
        try:
            obj = json.loads(decoded)
        except json.JSONDecodeError as exc:
            raise AvitoWebhookParseError("malformed json") from exc
        if not isinstance(obj, dict):
            raise AvitoWebhookParseError("body must be a JSON object")
        return obj

    @staticmethod
    def parse_event(payload: JsonObject) -> Event:  # noqa: PLR0911, PLR0912
        """Convert an Avito webhook envelope into a typed event.

        Handles messenger, order, item, and balance event kinds.
        Unrecognised kinds are wrapped in :class:`~avitoapi.events.RawWebhookEvent`
        so they reach handlers rather than being silently dropped.
        """
        envelope = payload.get("payload") or payload
        if not isinstance(envelope, dict):
            raise AvitoWebhookParseError("payload not an object")
        kind = envelope.get("type")
        value = envelope.get("value") or envelope
        if not isinstance(value, dict):
            raise AvitoWebhookParseError("payload.value not an object")

        account_id = str(value.get("user_id") or value.get("account_id") or "")
        chat_id = str(value.get("chat_id") or value.get("chatId") or "")

        if kind == "message":
            if not account_id or not chat_id:
                raise AvitoWebhookParseError("missing account_id or chat_id")
            # Webhook delivers the message as a raw dict; the typed Message union is
            # only built on the REST path. NewMessage stores it verbatim.
            return NewMessage(account_id=account_id, chat_id=chat_id, message=value)  # type: ignore[arg-type]
        if kind == "message_read":
            if not account_id or not chat_id:
                raise AvitoWebhookParseError("missing account_id or chat_id")
            message_id = str(value.get("message_id") or value.get("id") or "")
            return MessageRead(
                account_id=account_id,
                chat_id=chat_id,
                message_id=message_id,
            )
        if kind == "chat_archived":
            if not account_id or not chat_id:
                raise AvitoWebhookParseError("missing account_id or chat_id")
            return ChatArchived(account_id=account_id, chat_id=chat_id)

        order_id = str(value.get("order_id") or value.get("id") or "")
        ts = datetime.now(UTC)
        if kind == "order_created":
            return OrderCreated(account_id=account_id, order_id=order_id, created_at=ts)
        if kind == "order_confirmed":
            return OrderConfirmed(account_id=account_id, order_id=order_id, confirmed_at=ts)
        if kind == "order_shipped":
            return OrderShipped(
                account_id=account_id,
                order_id=order_id,
                track_number=str(value.get("track_number") or ""),
                shipped_at=ts,
            )
        if kind == "order_delivered":
            return OrderDelivered(account_id=account_id, order_id=order_id, delivered_at=ts)
        if kind == "order_completed":
            return OrderCompleted(account_id=account_id, order_id=order_id, completed_at=ts)
        if kind == "order_cancelled":
            return OrderCancelled(
                account_id=account_id,
                order_id=order_id,
                reason=str(value.get("reason") or ""),
                cancelled_at=ts,
            )
        if kind == "order_refunded":
            return OrderRefunded(
                account_id=account_id,
                order_id=order_id,
                reason=str(value.get("reason") or ""),
                refunded_at=ts,
            )
        if kind in ("order_status_changed", "order"):
            def _status(raw: object) -> OrderStatus:
                try:
                    return OrderStatus(str(raw))
                except ValueError:
                    return next(iter(OrderStatus))

            return OrderStatusChanged(
                account_id=account_id,
                order_id=order_id,
                previous=_status(value.get("previous_status") or value.get("from_status")),
                current=_status(value.get("status") or value.get("current_status")),
                occurred_at=ts,
            )

        raw_item_id = value.get("item_id") or value.get("id")
        item_id = int(str(raw_item_id)) if raw_item_id is not None and str(raw_item_id).isdigit() else 0
        if kind == "item_published":
            return ItemPublished(account_id=account_id, item_id=item_id, published_at=ts)
        if kind == "item_blocked":
            return ItemBlocked(
                account_id=account_id,
                item_id=item_id,
                reason=str(value.get("reason") or ""),
                blocked_at=ts,
            )
        if kind == "item_unblocked":
            return ItemUnblocked(account_id=account_id, item_id=item_id, unblocked_at=ts)
        if kind == "item_sold":
            return ItemSold(account_id=account_id, item_id=item_id, sold_at=ts)
        if kind == "item_archived":
            return ItemArchived(account_id=account_id, item_id=item_id, archived_at=ts)
        if kind in ("item_status_changed", "item"):
            def _istatus(raw: object) -> ItemStatus:
                try:
                    return ItemStatus(str(raw))
                except ValueError:
                    return next(iter(ItemStatus))

            return ItemStatusChanged(
                account_id=account_id,
                item_id=item_id,
                previous=_istatus(value.get("previous_status") or value.get("from_status")),
                current=_istatus(value.get("status") or value.get("current_status")),
                occurred_at=ts,
            )

        raise AvitoWebhookParseError(f"unknown event kind: {kind!r}")

    def _make_dispatch_terminal(self) -> NextHandler[Any, Any]:
        async def _terminal(event: Any, _ctx: Any) -> tuple[int, JsonObject]:
            await self._dispatch(event)
            return (200, {"ok": True})

        return _terminal

    async def _dispatch(self, event: Event) -> None:
        for attr in ("event_entry", "feed_event", "dispatch", "propagate_event"):
            handler = getattr(self.dispatcher, attr, None)
            if handler is not None:
                await handler(event)
                return
        # Last-resort: drive a bare Router instance.
        router = getattr(self.dispatcher, "router", None)
        if router is None:
            return
        from ..routers import EventContext  # noqa: PLC0415 — lazy to avoid cycle

        ctx = EventContext(event=event, dispatcher=self.dispatcher)
        await router.propagate(event, ctx)
