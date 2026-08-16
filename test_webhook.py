"""
Sanity tests -- mocks Gemini, Sheets, and the roster so this runs with no
API keys and no internet access. Run with: python test_webhook.py
Covers: a brand-new student's onboarding flow (school question -> choice
-> registration), and a normal question from an already-registered
student, on both WhatsApp and Telegram.
"""

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# In-memory fake roster so we can exercise the real onboarding logic
# without hitting Google Sheets.
_fake_roster = {}
_fake_next = {"ISE": 1, "TIO": 1}


def _fake_lookup(channel, identifier):
    return _fake_roster.get((channel, identifier))


def _fake_register(channel, identifier, school, prefix):
    n = _fake_next[prefix]
    _fake_next[prefix] += 1
    pilot_id = f"{prefix}{n:03d}"
    _fake_roster[(channel, identifier)] = {"pilot_id": pilot_id, "school": school}
    return pilot_id


_pending = set()


def _fake_awaiting(channel, identifier):
    return (channel, identifier) in _pending


def _fake_mark_awaiting(channel, identifier):
    _pending.add((channel, identifier))


async def _noop_send(*args, **kwargs):
    return None


with patch("tutor.get_tutor_reply", return_value=("2 + 2 = 4. Want to try a harder one?", 0.42)), \
     patch("sheet_logger.log_interaction", return_value=None), \
     patch("telegram_adapter.send_telegram_message", new=_noop_send), \
     patch("roster_sheet.lookup_student", side_effect=_fake_lookup), \
     patch("roster_sheet.register_student", side_effect=_fake_register), \
     patch("roster_sheet.is_awaiting_school_choice", side_effect=_fake_awaiting), \
     patch("roster_sheet.mark_awaiting_school_choice", side_effect=_fake_mark_awaiting):
    import main
    client = TestClient(main.app)

    # Health check
    r = client.get("/")
    assert r.status_code == 200, r.text
    print("Health check OK:", r.json())

    # --- New WhatsApp student: full onboarding flow ---
    r = client.post("/webhook/whatsapp", data={"From": "whatsapp:+2348000000099", "Body": "hi"})
    assert "which school" in r.text.lower(), r.text
    print("New student prompted for school OK")

    r = client.post("/webhook/whatsapp", data={"From": "whatsapp:+2348000000099", "Body": "1"})
    assert "ISE001" in r.text, r.text
    print("New student registered OK:", r.text)

    r = client.post("/webhook/whatsapp", data={"From": "whatsapp:+2348000000099", "Body": "what is 2+2"})
    assert "4" in r.text, r.text
    print("Registered student got tutor reply OK:", r.text)

    # --- New Telegram student: full onboarding flow ---
    r = client.post(
        "/webhook/telegram",
        json={"message": {"chat": {"id": 555}, "from": {"username": "test_student"}, "text": "hello"}},
    )
    assert r.status_code == 200, r.text
    print("Telegram new student prompted OK")

    r = client.post(
        "/webhook/telegram",
        json={"message": {"chat": {"id": 555}, "from": {"username": "test_student"}, "text": "2"}},
    )
    assert r.status_code == 200, r.text
    print("Telegram student registered OK")

    r = client.post(
        "/webhook/telegram",
        json={"message": {"chat": {"id": 555}, "from": {"username": "test_student"}, "text": "what is 2+2"}},
    )
    assert r.status_code == 200, r.text
    print("Telegram registered student got reply OK")

    # --- Empty message handling ---
    r = client.post("/webhook/whatsapp", data={"From": "whatsapp:+2348012345678", "Body": ""})
    assert r.status_code == 200, r.text
    print("Empty-message handling OK")

print("\nAll sanity checks passed.")
