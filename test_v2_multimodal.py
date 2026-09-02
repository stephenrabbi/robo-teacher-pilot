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

async def test_download_contract():
    # httpx Response methods/properties are synchronous even when the client call is async.
    fake_meta = MagicMock()
    fake_meta.is_success = True
    fake_meta.json.return_value = {"ok": True, "result": {"file_path": "photos/test.jpg"}}

    fake_image = MagicMock()
    fake_image.is_success = True
    fake_image.status_code = 200
    fake_image.content = b"jpeg-bytes"

    fake_client = AsyncMock()
    fake_client.__aenter__.return_value = fake_client
    fake_client.__aexit__.return_value = None
    fake_client.post.return_value = fake_meta
    fake_client.get.return_value = fake_image

    with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "test-token"}), patch("telegram_adapter.httpx.AsyncClient", return_value=fake_client):
        data, mime = await telegram_adapter.download_telegram_image("file123")
        assert data == b"jpeg-bytes"
        assert mime == "image/jpeg"

asyncio.run(test_download_contract())
print("V2 multimodal safety tests passed.")
