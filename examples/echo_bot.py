"""Echo bot: reply to every inbound message with the same text.

In production, call ``handler.handle(request_body)`` from your web framework's
webhook route. Here we feed one sample payload so the file runs standalone.
"""

import asyncio

from avitoapi import Client, ClientConfig, make_dispatcher
from avitoapi.events.messenger import NewMessage
from avitoapi.web import AvitoWebhookHandler

client = Client(config=ClientConfig(client_id="CLIENT_ID", client_secret="SECRET"), account_id="42")
dp = make_dispatcher(accounts=[client])


@dp.new_message()
async def echo(event: NewMessage, _ctx: object) -> None:
    text = event.message.get("text", "") if isinstance(event.message, dict) else ""
    if text:
        await client.send_message(chat_id=event.chat_id, text=text)


sample = {"type": "message", "value": {"user_id": "42", "chat_id": "7", "id": "1", "text": "hi"}}
asyncio.run(AvitoWebhookHandler(dp).handle(sample))
