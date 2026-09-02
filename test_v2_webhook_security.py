"""Security tests for Telegram webhook authentication.

These tests use FastAPI's in-process TestClient. They do not call Telegram,
Gemini, Google Sheets, or the live Render staging endpoint.
"""

import os
from unittest.mock import patch

from fastapi.testclient import TestClient

import main

TEST_SECRET = "unit-test-telegram-secret_2026"
PAYLOAD = {"update_id": 1}


def _client():
    return TestClient(main.app)


def test_missing_secret_header_is_rejected():
    with patch.dict(os.environ, {"TELEGRAM_WEBHOOK_SECRET": TEST_SECRET}):
        response = _client().post("/webhook/telegram", json=PAYLOAD)
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid Telegram webhook secret"


def test_wrong_secret_header_is_rejected():
    with patch.dict(os.environ, {"TELEGRAM_WEBHOOK_SECRET": TEST_SECRET}):
        response = _client().post(
            "/webhook/telegram",
            json=PAYLOAD,
            headers={"X-Telegram-Bot-Api-Secret-Token": "definitely-wrong"},
        )
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid Telegram webhook secret"


def test_correct_secret_header_is_accepted():
    with patch.dict(os.environ, {"TELEGRAM_WEBHOOK_SECRET": TEST_SECRET}):
        response = _client().post(
            "/webhook/telegram",
            json=PAYLOAD,
            headers={"X-Telegram-Bot-Api-Secret-Token": TEST_SECRET},
        )
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_unconfigured_webhook_auth_fails_closed():
    with patch.dict(os.environ, {}, clear=False):
        previous = os.environ.pop("TELEGRAM_WEBHOOK_SECRET", None)
        try:
            response = _client().post("/webhook/telegram", json=PAYLOAD)
        finally:
            if previous is not None:
                os.environ["TELEGRAM_WEBHOOK_SECRET"] = previous
    assert response.status_code == 500
    assert response.json()["detail"] == "Telegram webhook authentication is not configured"


test_missing_secret_header_is_rejected()
test_wrong_secret_header_is_rejected()
test_correct_secret_header_is_accepted()
test_unconfigured_webhook_auth_fails_closed()
print("V2 Telegram webhook authentication tests passed.")
