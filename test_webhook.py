"""Sanity tests for onboarding, tutoring, arithmetic guardrails, and webhooks."""

import os
from unittest.mock import patch
from fastapi.testclient import TestClient

_fake_roster = {}
_fake_next = {"ISE": 1, "TIO": 1}
_pending = set()
_sent_telegram = []


def _fake_lookup(channel, identifier):
    return _fake_roster.get((channel, identifier))


def _fake_register(channel, identifier, school, prefix):
    n = _fake_next[prefix]
    _fake_next[prefix] += 1
    pilot_id = f"{prefix}{n:03d}"
    _fake_roster[(channel, identifier)] = {"pilot_id": pilot_id, "school": school}
    return pilot_id


def _fake_awaiting(channel, identifier):
    return (channel, identifier) in _pending


def _fake_mark_awaiting(channel, identifier):
    _pending.add((channel, identifier))


async def _fake_send_telegram_message(chat_id, text):
    _sent_telegram.append((chat_id, text))


with patch.dict(os.environ, {
    "TWILIO_AUTH_TOKEN": "test-twilio-auth-token",
    "TELEGRAM_WEBHOOK_SECRET": "test-telegram-webhook-secret",
    "ALLOW_AUTO_ENROLL": "true",
    "WHATSAPP_MIGRATION_MODE": "false",
}, clear=False), \
     patch("tutor.get_tutor_reply", return_value=("2 + 2 = 4. Want to try a harder one?", 0.42)), \
     patch("sheet_logger.log_interaction", return_value=None), \
     patch("telegram_adapter.send_telegram_message", new=_fake_send_telegram_message), \
     patch("roster_sheet.lookup_student", side_effect=_fake_lookup), \
     patch("roster_sheet.register_student", side_effect=_fake_register), \
     patch("roster_sheet.is_awaiting_school_choice", side_effect=_fake_awaiting), \
     patch("roster_sheet.mark_awaiting_school_choice", side_effect=_fake_mark_awaiting):
    import main
    from roster_sheet import ONBOARDING_PROMPT, ENROLLMENT_CLOSED_PROMPT
    from tutor import _simple_arithmetic_answer

    client = TestClient(main.app)
    assert client.get("/").status_code == 200

    # Arithmetic guardrail is deterministic and does not require Gemini.
    assert "42" in _simple_arithmetic_answer("What is 19 + 23?")
    assert _simple_arithmetic_answer("Tell me about physics") is None
    print("Arithmetic guardrail OK")

    # Invalid webhook authentication is rejected.
    with patch.object(main.RequestValidator, "validate", return_value=False):
        r = client.post("/webhook/whatsapp", data={"From": "whatsapp:+2348000000099", "Body": "hi"})
        assert r.status_code == 403, r.text
    r = client.post("/webhook/telegram", headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-secret"}, json={"message": {"chat": {"id": 555}, "from": {"username": "test_student"}, "text": "hello"}})
    assert r.status_code == 403, r.text
    print("Webhook authentication rejection OK")

    # Migration mode bypasses Gemini/onboarding and sends only the Telegram handoff.
    with patch.object(main.RequestValidator, "validate", return_value=True), \
         patch.dict(os.environ, {"WHATSAPP_MIGRATION_MODE": "true"}, clear=False):
        r = client.post("/webhook/whatsapp", data={"From": "whatsapp:+2348000000099", "Body": "what is 2+2"})
        assert r.status_code == 200
        assert "RoboTeacherAfricaBot" in r.text, r.text
        assert "pilot has now ended" in r.text.lower(), r.text
    print("WhatsApp migration handoff OK")

    with patch.object(main.RequestValidator, "validate", return_value=True):
        r = client.post("/webhook/whatsapp", data={"From": "whatsapp:+2348000000099", "Body": "hi"})
        assert "which school" in r.text.lower(), r.text
        r = client.post("/webhook/whatsapp", data={"From": "whatsapp:+2348000000099", "Body": "1"})
        assert "ISE001" in r.text, r.text
        r = client.post("/webhook/whatsapp", data={"From": "whatsapp:+2348000000099", "Body": "what is 2+2"})
        assert "4" in r.text, r.text
        r = client.post("/webhook/whatsapp", data={"From": "whatsapp:+2348012345678", "Body": ""})
        assert r.status_code == 200
    print("WhatsApp onboarding and tutoring OK")

    telegram_headers = {"X-Telegram-Bot-Api-Secret-Token": "test-telegram-webhook-secret"}
    r = client.post("/webhook/telegram", headers=telegram_headers, json={"message": {"chat": {"id": 555}, "from": {"username": "test_student"}, "text": "hello"}})
    assert r.status_code == 200 and _sent_telegram[-1] == (555, ONBOARDING_PROMPT)
    r = client.post("/webhook/telegram", headers=telegram_headers, json={"message": {"chat": {"id": 555}, "from": {"username": "test_student"}, "text": "2"}})
    assert "TIO001" in _sent_telegram[-1][1]
    r = client.post("/webhook/telegram", headers=telegram_headers, json={"message": {"chat": {"id": 555}, "from": {"username": "test_student"}, "text": "what is 2+2"}})
    assert _sent_telegram[-1] == (555, "2 + 2 = 4. Want to try a harder one?")
    print("Telegram onboarding and tutoring OK")

    # Closed-pilot mode blocks unknown identifiers while existing roster users work.
    with patch("main.auto_enrollment_enabled", return_value=False):
        outcome = main._get_or_onboard("telegram", "unknown_student", "hello")
        assert outcome == ("reply", ENROLLMENT_CLOSED_PROMPT)
    print("Closed enrollment guardrail OK")

print("\nAll sanity checks passed.")
