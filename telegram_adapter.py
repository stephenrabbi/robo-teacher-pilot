"""Thin adapter for the Telegram Bot API.

V2 adds bounded image and voice-note download support for multimodal tutoring
while keeping bot credentials out of logs and never persisting learner media.
"""

import logging
import os
import re
import httpx

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

_TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"
_TELEGRAM_FILE_API = "https://api.telegram.org/file/bot{token}/{file_path}"
_WEBHOOK_SECRET_RE = re.compile(r"^[A-Za-z0-9_-]{1,256}$")
MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_AUDIO_BYTES = 12 * 1024 * 1024
SUPPORTED_AUDIO_MIME_TYPES = {
    "audio/ogg", "audio/opus", "audio/mpeg", "audio/mp3", "audio/wav",
    "audio/x-wav", "audio/aac", "audio/flac", "audio/m4a", "audio/webm",
}


def _telegram_error(resp: httpx.Response, operation: str) -> RuntimeError:
    """Return a credential-safe Telegram API error without exposing tokenized URLs."""
    description = "Telegram API request failed"
    try:
        payload = resp.json()
        if isinstance(payload, dict) and payload.get("description"):
            description = str(payload["description"])
    except Exception:
        pass
    return RuntimeError(f"{operation} failed ({resp.status_code}): {description}")


def _ensure_telegram_ok(resp: httpx.Response, operation: str) -> dict:
    if not resp.is_success:
        raise _telegram_error(resp, operation) from None
    try:
        payload = resp.json()
    except Exception:
        raise RuntimeError(f"{operation} failed: Telegram returned an invalid response") from None
    if not isinstance(payload, dict) or not payload.get("ok"):
        description = payload.get("description", "Telegram API request failed") if isinstance(payload, dict) else "Telegram API request failed"
        raise RuntimeError(f"{operation} failed: {description}") from None
    return payload


async def configure_telegram_webhook() -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    secret = os.environ["TELEGRAM_WEBHOOK_SECRET"]
    if not _WEBHOOK_SECRET_RE.fullmatch(secret):
        raise ValueError("TELEGRAM_WEBHOOK_SECRET must be 1-256 characters using only letters, numbers, underscore, or hyphen")
    webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL", "https://robo-teacher-jfg7.onrender.com/webhook/telegram")
    url = _TELEGRAM_API.format(token=token, method="setWebhook")
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json={"url": webhook_url, "secret_token": secret, "drop_pending_updates": False})
        _ensure_telegram_ok(resp, "Telegram webhook registration")


async def send_telegram_message(chat_id: int | str, text: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    url = _TELEGRAM_API.format(token=token, method="sendMessage")
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json={"chat_id": chat_id, "text": text})
        _ensure_telegram_ok(resp, "Telegram message send")


async def _download_telegram_file(file_id: str, max_bytes: int) -> tuple[bytes, str]:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    get_file_url = _TELEGRAM_API.format(token=token, method="getFile")
    async with httpx.AsyncClient(timeout=30) as client:
        meta_resp = await client.post(get_file_url, json={"file_id": file_id})
        payload = _ensure_telegram_ok(meta_resp, "Telegram file lookup")
        file_path = payload.get("result", {}).get("file_path")
        if not file_path:
            raise RuntimeError("Telegram did not return a downloadable file path")
        file_url = _TELEGRAM_FILE_API.format(token=token, file_path=file_path)
        media_resp = await client.get(file_url)
        if not media_resp.is_success:
            raise RuntimeError(f"Telegram media download failed ({media_resp.status_code})") from None
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
