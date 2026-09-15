"""Regression tests for Practice Mode request recovery and state reconciliation."""

from pathlib import Path

from fastapi.testclient import TestClient

import classroom_api
import practice
from main import app


client = TestClient(app)


def _reset_state():
    classroom_api._classroom_profiles.clear()
    classroom_api._request_times.clear()
    practice._sessions.clear()


def _session(learner_key: str) -> dict:
    response = client.post(
        "/api/classroom/session",
        json={"learner_key": learner_key, "nickname": "Practice Learner", "class_level": "JSS2"},
    )
    assert response.status_code == 200
    return response.json()


def _start(session_token: str) -> dict:
    response = client.post(
        "/api/classroom/practice/start",
        json={
            "session_token": session_token,
            "topic": "Whole Numbers",
            "difficulty": "Easy",
            "question_count": 5,
            "class_level": "JSS2",
            "language": "English",
        },
    )
    assert response.status_code == 200
    return response.json()


def _snapshot(session_token: str) -> dict:
    response = client.post(
        "/api/classroom/practice/language",
        json={"session_token": session_token, "language": "English"},
    )
    assert response.status_code == 200
    return response.json()


def test_language_endpoint_can_reconstruct_answered_practice_state():
    _reset_state()
    session = _session("a" * 48)
    first = _start(session["session_token"])

    answer = client.post(
        "/api/classroom/practice/answer",
        json={"session_token": session["session_token"], "answer": "definitely-wrong"},
    )
    assert answer.status_code == 200
    checked = answer.json()

    snapshot = _snapshot(session["session_token"])
    assert snapshot["session_id"] == first["session_id"]
    assert snapshot["question_number"] == 1
    assert snapshot["attempted"] == 1
    assert snapshot["answered"] is True
    assert snapshot["feedback"]["correct"] == checked["correct"]
    assert snapshot["feedback"]["explanation"] == checked["explanation"]


def test_language_endpoint_can_reconstruct_advanced_question_state():
    _reset_state()
    session = _session("b" * 48)
    _start(session["session_token"])
    client.post(
        "/api/classroom/practice/answer",
        json={"session_token": session["session_token"], "answer": "definitely-wrong"},
    )
    advanced = client.post(
        "/api/classroom/practice/next",
        json={"session_token": session["session_token"]},
    )
    assert advanced.status_code == 200

    snapshot = _snapshot(session["session_token"])
    assert snapshot["answered"] is False
    assert snapshot["question_number"] == 2
    assert snapshot["question"] == advanced.json()["question"]


def test_completed_practice_snapshot_contains_results_for_recovery():
    _reset_state()
    session = _session("c" * 48)
    _start(session["session_token"])

    for index in range(5):
        answer = client.post(
            "/api/classroom/practice/answer",
            json={"session_token": session["session_token"], "answer": "definitely-wrong"},
        )
        assert answer.status_code == 200
        if index < 4:
            next_response = client.post(
                "/api/classroom/practice/next",
                json={"session_token": session["session_token"]},
            )
            assert next_response.status_code == 200

    snapshot = _snapshot(session["session_token"])
    assert snapshot["answered"] is True
    assert snapshot["attempted"] == 5
    assert snapshot["summary"]["attempted"] == 5
    assert snapshot["summary"]["session_id"] == snapshot["session_id"]


def test_browser_recovery_only_reconciles_answer_and_next_requests():
    loader = Path("classroom/practice_feedback.js").read_text(encoding="utf-8")
    script = Path("classroom/practice_reliability.js").read_text(encoding="utf-8")

    assert "practice_reliability.js?v=20260915-practice-reliability1" in loader
    assert "RECOVERABLE_ACTIONS = new Set(['answer', 'next'])" in script
    assert "`${PRACTICE_PATH}language`" in script
    assert "response.status !== 409" in script
    assert "X-Robo-Teacher-Recovered" in script
    assert "never resend the learner's answer automatically" in script


def test_browser_recovery_does_not_persist_answer_content():
    script = Path("classroom/practice_reliability.js").read_text(encoding="utf-8")
    assert "localStorage" not in script
    assert "sessionStorage" not in script
    assert "indexedDB" not in script
    assert "learner_answer" not in script
