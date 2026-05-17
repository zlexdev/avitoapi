"""HTTP-agnostic Avito webhook adapter.

Parses an Avito messenger webhook body (dict) into a typed
:class:`~avitoapi.events.NewMessage` / :class:`~avitoapi.events.MessageRead` /
:class:`~avitoapi.events.ChatArchived` event and forwards it into a
Dispatcher (or fallback router).

The handler intentionally accepts a plain ``dict`` instead of an
``aiohttp.web.Request`` so it can be unit-tested without aiohttp. The
production aiohttp wiring lives in ``examples/echo_bot/``.
"""
from __future__ import annotations

import json
from typing import Any

from ..events.messenger import ChatArchived, MessageRead, MessengerEvent, NewMessage


class AvitoWebhookParseError(ValueError):
    """Raised when the webhook body does not match an Avito payload shape."""


class AvitoWebhookHandler:
    """Adapter: Avito webhook JSON → typed event → Dispatcher.

    The dispatcher (or any object with a ``dispatch(event)`` / ``feed_event(event)``
    coroutine method) is invoked once per parsed event. Replies are JSON-serialisable
    ``(status_code, body)`` tuples — the caller is responsible for translating
    them into the framework-native response (aiohttp, FastAPI, Litestar).
    """

    def __init__(self, dispatcher: Any, *, mount_path: str = "/messenger") -> None:
        self.dispatcher = dispatcher
        self.mount_path = mount_path

    async def handle(
        self,
        body: bytes | str | dict[str, Any],
    ) -> tuple[int, dict[str, Any]]:
        """Parse, dispatch, return ``(status, body)``.

        * Valid payload → ``(200, {"ok": True})``.
        * Malformed JSON → ``(400, {"error": "invalid_body"})``.
        * Unknown event kind → ``(200, {"ok": True, "skipped": "<reason>"})``
          (Avito retries 4xx, and unknown kinds should not block).
        """
        try:
            payload = self._coerce_payload(body)
        except AvitoWebhookParseError:
            return (400, {"error": "invalid_body"})

        try:
            event = self.parse_event(payload)
        except AvitoWebhookParseError as exc:
            return (200, {"ok": True, "skipped": str(exc)})

        await self._dispatch(event)
        return (200, {"ok": True})

    @staticmethod
    def _coerce_payload(body: bytes | str | dict[str, Any]) -> dict[str, Any]:
        if isinstance(body, dict):
            return body
        if isinstance(body, (bytes, bytearray)):
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
    def parse_event(payload: dict[str, Any]) -> MessengerEvent:
        """Convert an Avito webhook envelope into a typed event.

        Avito's envelope: ``{"id": "...", "version": "v3.0.0",
        "timestamp": ..., "payload": {"type": "message", "value": {...}}}``.

        Recognised ``payload.type`` values: ``message``, ``message_read``,
        ``chat_archived``.
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
        if not account_id or not chat_id:
            raise AvitoWebhookParseError("missing account_id or chat_id")

        if kind == "message":
            return NewMessage(account_id=account_id, chat_id=chat_id, message=value)
        if kind == "message_read":
            message_id = str(value.get("message_id") or value.get("id") or "")
            return MessageRead(
                account_id=account_id,
                chat_id=chat_id,
                message_id=message_id,
            )
        if kind == "chat_archived":
            return ChatArchived(account_id=account_id, chat_id=chat_id)
        raise AvitoWebhookParseError(f"unknown event kind: {kind!r}")

    async def _dispatch(self, event: MessengerEvent) -> None:
        for attr in ("event_entry", "feed_event", "dispatch", "propagate_event"):
            handler = getattr(self.dispatcher, attr, None)
            if handler is not None:
                await handler(event)
                return
        # Last-resort: drive a bare router via the evented entry-point.
        router = getattr(self.dispatcher, "router", None)
        if router is None:
            return
        import evented  # noqa: PLC0415 — single-use, avoids a hard top-level dep on web handler

        ctx = evented.EventContext(event=event, dispatcher=self.dispatcher)
        await router.propagate(event, ctx)
