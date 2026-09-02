"""Offline safety/contract tests for Robo-Teacher V2 multimodal tutoring."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import telegram_adapter
import tutor

assert tutor.SUPPORTED_IMAGE_MIME_TYPES == {"image/jpeg", "image/png", "image/webp"}
assert tutor.MAX_IMAGE_BYTES <= 8 * 1024 * 1024

try:
    tutor.get_tutor_image_reply("TEST001", b"", "image/jpeg")
    raise AssertionError("Empty images must be rejected")
except ValueError:
    pass

try:
    tutor.get_tutor_image_reply("TEST001", b"abc", "application/pdf")
    raise AssertionError("Unsupported MIME types must be rejected")
except ValueError:
    pass

for bad_url in ("http://example.com/webhook", "not-a-url", ""):
    try:
        telegram_adapter._validate_webhook_url(bad_url)
        raise AssertionError("Non-HTTPS or malformed webhook URLs must be rejected")
    except ValueError:
        pass
telegram_adapter._validate_webhook_url("https://example.com/webhook")


class FakeStreamResponse:
    def __init__(self, chunks, status_code=200, headers=None):
        self._chunks = chunks
        self.status_code = status_code
        self.is_success = 200 <= status_code < 300
        self.headers = headers or {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def aiter_bytes(self):
        for chunk in self._chunks:
            yield chunk


async def test_download_contract():
    fake_meta = MagicMock()
    fake_meta.is_success = True
    fake_meta.json.return_value = {"ok": True, "result": {"file_path": "photos/test.jpg"}}

    fake_client = AsyncMock()
    fake_client.__aenter__.return_value = fake_client
    fake_client.__aexit__.return_value = None
    fake_client.post.return_value = fake_meta
    fake_client.stream = MagicMock(return_value=FakeStreamResponse([b"jpeg-", b"bytes"]))

    with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "test-token"}), patch("telegram_adapter.httpx.AsyncClient", return_value=fake_client):
        data, mime = await telegram_adapter.download_telegram_image("file123")
        assert data == b"jpeg-bytes"
        assert mime == "image/jpeg"


async def test_stream_limit():
    fake_meta = MagicMock()
    fake_meta.is_success = True
    fake_meta.json.return_value = {"ok": True, "result": {"file_path": "photos/test.jpg"}}

    fake_client = AsyncMock()
    fake_client.__aenter__.return_value = fake_client
    fake_client.__aexit__.return_value = None
    fake_client.post.return_value = fake_meta
    fake_client.stream = MagicMock(return_value=FakeStreamResponse([b"1234", b"5678"]))

    with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "test-token"}), patch("telegram_adapter.httpx.AsyncClient", return_value=fake_client):
        try:
            await telegram_adapter._download_telegram_file("file123", 6)
            raise AssertionError("Streaming download must stop when the byte limit is exceeded")
        except ValueError as exc:
            assert "too large" in str(exc)


asyncio.run(test_download_contract())
asyncio.run(test_stream_limit())
print("V2 multimodal safety tests passed.")
