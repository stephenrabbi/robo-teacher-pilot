"""
Quick sanity test — mocks Gemini and Sheets so it runs with no API keys
and no internet access. Run with: python test_webhook.py
This just proves the FastAPI/Twilio wiring is correct; it does not
test real Gemini answer quality (do that manually once deployed).
"""

from unittest.mock import patch
from fastapi.testclient import TestClient

import asyncio


async def _noop_send(*args, **kwargs):
    return None


with patch("tutor.get_tutor_reply", return_value=("2 + 2 = 4. Want to try a harder one?", 0.42)), \
     patch("sheet_logger.log_interaction", return_value=None), \
     patch("telegram_adapter.send_telegram_message", new=_noop_send), \
     patch("whatsapp_adapter.send_whatsapp_message", return_value=None):
    import main
    client = TestClient(main.app)

    # Health check
    r = client.get("/")
    assert r.status_code == 200, r.text
    print("Health check OK:", r.json())

    # Simulated incoming WhatsApp message from Twilio Sandbox
    r = client.post(
        "/webhook/whatsapp",
        data={"From": "whatsapp:+2348000000001", "Body": "what is 2+2"},
    )
    assert r.status_code == 200, r.text
    assert "4" in r.text, r.text
    print("Webhook reply OK, TwiML:\n", r.text)

    # Empty message should get the friendly prompt, not crash
    r = client.post("/webhook/whatsapp", data={"From": "whatsapp:+2348012345678", "Body": ""})
    assert r.status_code == 200, r.text
    print("Empty-message handling OK, TwiML:\n", r.text)

    # Simulated incoming Telegram update
    r = client.post(
        "/webhook/telegram",
        json={"message": {"chat": {"id": 100000001}, "from": {"username": "example_username_1"}, "text": "what is 2+2"}},
    )
    assert r.status_code == 200, r.text
    print("Telegram webhook accepted OK:", r.json())

print("\nAll sanity checks passed.")
