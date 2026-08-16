"""
Thin adapter for the Telegram Bot API. No phone/SMS verification gate —
just needs a bot token from @BotFather (see README).
"""

import os
import httpx

_TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


async def send_telegram_message(chat_id: int | str, text: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    url = _TELEGRAM_API.format(token=token, method="sendMessage")
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json={"chat_id": chat_id, "text": text})
        resp.raise_for_status()
