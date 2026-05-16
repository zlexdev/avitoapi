"""Entrypoint for the echo bot.

Usage:
    python -m echo_bot                          run the webhook server
    python -m echo_bot --register <https-url>   register the webhook URL with Avito
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from typing import Any

from avitoapi.client import Client
from avitoapi.config import ClientConfig
from avitoapi.events.messenger import NewMessage
from avitoapi.routers.messenger import MessengerRouter
from avitoapi.storage.memory import MemoryStorage
from avitoapi.web.avito_webhook_handler import AvitoWebhookHandler

from .dispatcher_factory import build
from .healthz import attach as attach_healthz

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def _load_accounts() -> list[Client]:
    """Read env and return one or more :class:`Client` instances."""
    ids_raw = os.environ.get("AVITO_ACCOUNT_IDS", "").strip()
    if ids_raw:
        clients: list[Client] = []
        for acc_id in (s.strip() for s in ids_raw.split(",") if s.strip()):
            client_id = os.environ.get(f"AVITO_CLIENT_ID_{acc_id}")
            client_secret = os.environ.get(f"AVITO_CLIENT_SECRET_{acc_id}")
            user_id_raw = os.environ.get(f"AVITO_USER_ID_{acc_id}")
            if not client_id or not client_secret:
                print(  # noqa: T201 — example app surface
                    f"[warn] skipping {acc_id}: missing AVITO_CLIENT_ID_{acc_id} "
                    f"or AVITO_CLIENT_SECRET_{acc_id}",
                    file=sys.stderr,
                )
                continue
            cfg_kwargs: dict[str, Any] = {
                "client_id": client_id,
                "client_secret": client_secret,
            }
            if user_id_raw:
                cfg_kwargs["user_id"] = int(user_id_raw)
            clients.append(Client(config=ClientConfig(**cfg_kwargs), account_id=acc_id))
        return clients
    cfg = ClientConfig.from_env()
    return [Client(config=cfg, account_id=os.environ.get("AVITO_USER_ID", "default"))]


def _build_router(accounts: dict[str, Client]) -> MessengerRouter:
    router = MessengerRouter()

    @router.new_message()
    async def echo(event: NewMessage) -> None:
        """Echo inbound text back to the sender."""
        chat_id = event.chat_id
        text = ""
        msg = event.message
        if isinstance(msg, dict):
            text = str(msg.get("text") or msg.get("content", {}).get("text") or "")
        if not text:
            return
        client = accounts.get(event.account_id)
        if client is None:
            return
        await client.send_text_message(chat_id=chat_id, text=text)

    return router


async def _serve() -> None:
    from aiohttp import web

    accounts = _load_accounts()
    if not accounts:
        print("[fatal] no accounts configured", file=sys.stderr)  # noqa: T201
        sys.exit(2)

    storage = MemoryStorage()
    webhook_secret = os.environ.get("AVITO_WEBHOOK_SECRET", "")
    if not webhook_secret:
        print(  # noqa: T201
            "[warn] AVITO_WEBHOOK_SECRET is empty — signature checks will fail",
            file=sys.stderr,
        )

    dispatcher, hmac_mw, idempotency_mw, fast_return_mw = build(
        accounts=accounts,
        storage=storage,
        webhook_secret=webhook_secret,
    )
    account_index = {acc.account_id or "_anon": acc for acc in accounts}
    dispatcher.include_router(_build_router(account_index))

    handler = AvitoWebhookHandler(dispatcher)

    async def webhook_handler(request: web.Request) -> web.Response:
        body = await request.read()
        signature = request.headers.get("x-avito-messenger-signature", "")
        webhook_id = request.match_info.get("webhook_id", "default")
        try:
            verified = await hmac_mw.verify(body, signature, webhook_id)
        except Exception:  # noqa: BLE001 — surface as 401 to the upstream
            return web.json_response({"error": "missing_signature"}, status=401)
        if not verified:
            return web.json_response({"error": "bad_signature"}, status=401)

        payload = handler._coerce_payload(body)
        try:
            event = handler.parse_event(payload)
        except Exception as exc:  # noqa: BLE001 — surface parser failure as 400
            return web.json_response({"error": "parse_failed", "detail": str(exc)}, status=400)

        if isinstance(event, NewMessage):
            msg = event.message
            message_id = ""
            if isinstance(msg, dict):
                message_id = str(msg.get("id") or msg.get("message_id") or "")
            if message_id and await idempotency_mw.seen(event.chat_id, message_id):
                return web.json_response({"ok": True, "deduped": True})

        fast_return_mw.schedule(handler._dispatch(event))
        return web.json_response({"ok": True})

    path = os.environ.get("WEBHOOK_PATH", "/messenger")
    app = web.Application()
    app.router.add_post(path, webhook_handler)
    attach_healthz(app)

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8080"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    print(f"[ok] listening on http://{host}:{port}{path}")  # noqa: T201
    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()
        for client in accounts:
            await client.close()


def _register(url: str) -> None:
    """One-shot: register the webhook URL with Avito.

    ``POST /messenger/v3/webhook`` is not yet wrapped in :class:`Client`;
    this prints the would-be call so deploys aren't blocked. Wire to the
    real subscribe method once it lands.
    """
    secret = os.environ.get("AVITO_WEBHOOK_SECRET", "<missing>")
    print(  # noqa: T201
        f"[register] would POST /messenger/v3/webhook url={url} secret={secret!r}",
    )


def main() -> None:
    parser = argparse.ArgumentParser(prog="echo_bot")
    parser.add_argument("--register", metavar="URL", help="Register webhook URL with Avito and exit.")
    args = parser.parse_args()
    if args.register:
        _register(args.register)
        return
    asyncio.run(_serve())


if __name__ == "__main__":
    main()
