"""Focused tests for durable cross-session mastery memory."""

from unittest.mock import patch

from fastapi.testclient import TestClient

import classroom_api
import mastery_progress
from main import app


client = TestClient(app)


def _reset_state():
    classroom_api._classroom_profiles.clear()
    classroom_api._request_times.clear()
    mastery_progress._memory_records.clear()
    mastery_progress._unsynced_ids.clear()


def _session(learner_key: str = "a" * 48, class_level: str = "JSS2") -> dict:
    response = client.post(
        "/api/classroom/session",
        json={"learner_key": learner_key, "nickname": "Learner", "class_level": class_level},
    )
    assert response.status_code == 200
    return response.json()


def _event(session: dict, check_id: str, correct: bool, stage: str, text: str) -> dict:
    with patch.object(mastery_progress, "_sheet_configured", return_value=False):
        response = client.post(
            "/api/classroom/mastery/event",
            json={
                "session_token": session["session_token"],
                "lesson_text": text,
                "topic_hint": "",
                "check_id": check_id,
                "stage": stage,
                "correct": correct,
            },
        )
    assert response.status_code == 200
    return response.json()


def test_topic_inference_uses_class_curriculum():
    assert mastery_progress.infer_topic(
        "To add fractions, first find a common denominator and add the numerators.",
        "JSS2",
    ) == "Fractions, Ratios, Decimals & Percentages"
    assert mastery_progress.infer_topic(
        "Use Pythagoras theorem to find the hypotenuse of the right triangle.",
        "JSS2",
    ) == "Pythagoras & Mensuration"
    assert mastery_progress.infer_topic(
        "Factorise the quadratic expression x squared plus five x plus six.",
        "JSS3",
    ) == "Factorisation & Quadratic Expressions"


def test_reteach_success_is_remembered_as_mastered_across_new_session():
    _reset_state()
    first = _session()
    lesson = "When adding fractions, use a common denominator before adding the numerators."
    wrong = _event(first, "1" * 32, False, "initial", lesson)
    assert wrong["stored"] is True
    assert wrong["state"] == "needs_support"

    mastered = _event(first, "2" * 32, True, "reteach", lesson)
    assert mastered["state"] == "mastered"
    assert mastered["topic"] == "Fractions, Ratios, Decimals & Percentages"

    second = _session()
    with patch.object(mastery_progress, "_sheet_configured", return_value=False):
        summary = client.post(
            "/api/classroom/mastery/summary",
            json={"session_token": second["session_token"], "class_level": "JSS2"},
        )
    assert summary.status_code == 200
    body = summary.json()
    assert "Fractions, Ratios, Decimals & Percentages" in body["mastered_topics"]
    assert body["needs_support_topics"] == []


def test_second_reteach_miss_is_remembered_as_needs_support():
    _reset_state()
    session = _session(learner_key="b" * 48)
    lesson = "Probability measures the chance that an outcome will happen."
    _event(session, "3" * 32, False, "initial", lesson)
    result = _event(session, "4" * 32, False, "reteach", lesson)
    assert result["state"] == "needs_support"
    assert result["summary"]["focus_topic"] == "Probability"
    assert result["summary"]["needs_support_topics"] == ["Probability"]


def test_mastery_storage_keeps_no_lesson_transcript():
    _reset_state()
    session = _session(learner_key="c" * 48, class_level="JSS3")
    lesson = "A deliberately unique private lesson sentence about simultaneous equations 84729."
    _event(session, "5" * 32, True, "reteach", lesson)
    assert len(mastery_progress._memory_records) == 1
    stored = mastery_progress._memory_records[0]
    assert "lesson_text" not in stored
    assert lesson not in repr(stored)
    assert stored["topic"] == "Simultaneous Equations"


def test_duplicate_check_event_is_idempotent():
    _reset_state()
    session = _session(learner_key="d" * 48)
    lesson = "Probability measures the chance that an outcome will happen."
    _event(session, "6" * 32, True, "initial", lesson)
    _event(session, "6" * 32, True, "initial", lesson)
    assert len(mastery_progress._memory_records) == 1
