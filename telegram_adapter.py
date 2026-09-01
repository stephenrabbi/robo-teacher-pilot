"""
Thin adapter for the Telegram Bot API. No phone/SMS verification gate —
just needs a bot token from @BotFather (see README).
"""

import logging
import os
import httpx

# Avoid leaking Telegram Bot API URLs (which contain the bot token) into logs.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

_TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


async def configure_telegram_webhook() -> None:
    """Register the Render Telegram webhook using the configured secret token.

    This keeps Telegram and Render's TELEGRAM_WEBHOOK_SECRET synchronized after
    deployments without exposing either secret in source control.
    """
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    secret = os.environ["TELEGRAM_WEBHOOK_SECRET"]
    webhook_url = os.getenv(
        "TELEGRAM_WEBHOOK_URL",
        "https://robo-teacher-jfg7.onrender.com/webhook/telegram",
    )
    url = _TELEGRAM_API.format(token=token, method="setWebhook")
    payload = {
        "url": webhook_url,
        "secret_token": secret,
        "drop_pending_updates": False,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("ok"):
            raise RuntimeError("Telegram webhook registration failed")


async def send_telegram_message(chat_id: int | str, text: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    url = _TELEGRAM_API.format(token=token, method="sendMessage")
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json={"chat_id": chat_id, "text": text})
        resp.raise_for_status()
