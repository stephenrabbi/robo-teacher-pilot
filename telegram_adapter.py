"""Thin adapter for the Telegram Bot API.

V2 adds bounded image download support for multimodal tutoring while keeping bot
credentials out of logs and never persisting learner images to disk.
"""

import logging
import os
import httpx

# Avoid leaking Telegram Bot API URLs (which contain the bot token) into logs.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

_TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"
_TELEGRAM_FILE_API = "https://api.telegram.org/file/bot{token}/{file_path}"
MAX_IMAGE_BYTES = 8 * 1024 * 1024


async def configure_telegram_webhook() -> None:
    """Register the Render Telegram webhook using the configured secret token."""
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


async def download_telegram_image(file_id: str) -> tuple[bytes, str]:
    """Download one Telegram image into memory with a strict size bound.

    The bytes are returned directly to the tutor and are not written to disk.
    Telegram photos are JPEG; image documents may also be PNG or WEBP.
    """
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    get_file_url = _TELEGRAM_API.format(token=token, method="getFile")
    async with httpx.AsyncClient(timeout=30) as client:
        meta_resp = await client.post(get_file_url, json={"file_id": file_id})
        meta_resp.raise_for_status()
        payload = meta_resp.json()
        if not payload.get("ok") or not payload.get("result", {}).get("file_path"):
            raise RuntimeError("Telegram did not return a downloadable file path")
        file_path = payload["result"]["file_path"]
        file_url = _TELEGRAM_FILE_API.format(token=token, file_path=file_path)
        image_resp = await client.get(file_url)
        image_resp.raise_for_status()
        image_bytes = image_resp.content

    if not image_bytes:
        raise ValueError("The uploaded image was empty")
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise ValueError("The uploaded image is too large")

    suffix = file_path.lower().rsplit(".", 1)[-1] if "." in file_path else "jpg"
    mime_type = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
    }.get(suffix, "image/jpeg")
    return image_bytes, mime_type
