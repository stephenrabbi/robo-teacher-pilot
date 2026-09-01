"""Thin adapter for the Telegram Bot API.

V2 adds bounded image and voice-note download support for multimodal tutoring
while keeping bot credentials out of logs and never persisting learner media.
"""

import logging
import os
import httpx

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

_TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"
_TELEGRAM_FILE_API = "https://api.telegram.org/file/bot{token}/{file_path}"
MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_AUDIO_BYTES = 12 * 1024 * 1024
SUPPORTED_AUDIO_MIME_TYPES = {
    "audio/ogg", "audio/opus", "audio/mpeg", "audio/mp3", "audio/wav",
    "audio/x-wav", "audio/aac", "audio/flac", "audio/m4a", "audio/webm",
}


async def configure_telegram_webhook() -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    secret = os.environ["TELEGRAM_WEBHOOK_SECRET"]
    webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL", "https://robo-teacher-jfg7.onrender.com/webhook/telegram")
    url = _TELEGRAM_API.format(token=token, method="setWebhook")
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json={"url": webhook_url, "secret_token": secret, "drop_pending_updates": False})
        resp.raise_for_status()
        if not resp.json().get("ok"):
            raise RuntimeError("Telegram webhook registration failed")


async def send_telegram_message(chat_id: int | str, text: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    url = _TELEGRAM_API.format(token=token, method="sendMessage")
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json={"chat_id": chat_id, "text": text})
        resp.raise_for_status()


async def _download_telegram_file(file_id: str, max_bytes: int) -> tuple[bytes, str]:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    get_file_url = _TELEGRAM_API.format(token=token, method="getFile")
    async with httpx.AsyncClient(timeout=30) as client:
        meta_resp = await client.post(get_file_url, json={"file_id": file_id})
        meta_resp.raise_for_status()
        payload = meta_resp.json()
        file_path = payload.get("result", {}).get("file_path") if payload.get("ok") else None
        if not file_path:
            raise RuntimeError("Telegram did not return a downloadable file path")
        file_url = _TELEGRAM_FILE_API.format(token=token, file_path=file_path)
        media_resp = await client.get(file_url)
        media_resp.raise_for_status()
        media_bytes = media_resp.content
    if not media_bytes:
        raise ValueError("The uploaded file was empty")
    if len(media_bytes) > max_bytes:
        raise ValueError("The uploaded file is too large")
    return media_bytes, file_path


async def download_telegram_image(file_id: str) -> tuple[bytes, str]:
    image_bytes, file_path = await _download_telegram_file(file_id, MAX_IMAGE_BYTES)
    suffix = file_path.lower().rsplit(".", 1)[-1] if "." in file_path else "jpg"
    mime_type = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(suffix, "image/jpeg")
    return image_bytes, mime_type


async def download_telegram_audio(file_id: str, declared_mime_type: str = "") -> tuple[bytes, str]:
    """Download a Telegram voice/audio file transiently with a strict size bound."""
    audio_bytes, file_path = await _download_telegram_file(file_id, MAX_AUDIO_BYTES)
    suffix = file_path.lower().rsplit(".", 1)[-1] if "." in file_path else "ogg"
    inferred = {
        "ogg": "audio/ogg", "oga": "audio/ogg", "opus": "audio/opus",
        "mp3": "audio/mp3", "mpeg": "audio/mpeg", "wav": "audio/wav",
        "aac": "audio/aac", "flac": "audio/flac", "m4a": "audio/m4a", "webm": "audio/webm",
    }.get(suffix, "audio/ogg")
    mime_type = declared_mime_type if declared_mime_type in SUPPORTED_AUDIO_MIME_TYPES else inferred
    if mime_type not in SUPPORTED_AUDIO_MIME_TYPES:
        raise ValueError("Unsupported audio type")
    return audio_bytes, mime_type
