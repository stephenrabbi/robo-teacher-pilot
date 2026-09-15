"""Focused tests for adaptive reteaching after Check Understanding."""
from unittest.mock import patch

from fastapi.testclient import TestClient

import classroom_api
from v25_app import app


client = TestClient(app)


def _reset_state():
    classroom_api._understanding_checks.clear()
    classroom_api._request_times.clear()


def _start_check(session: dict, lesson: str, language: str = "English") -> dict:
    generated = {
        "question": "What is 2 + 2?",
        "choices": ["3", "4", "5"],
        "correct_index": 1,
        "feedback": "Add the two values to get 4.",
    }
    with patch.object(classroom_api, "generate_understanding_check", return_value=generated):
        response = client.post(
            "/api/classroom/understanding/start",
            json={"session_token": session["session_token"], "text": lesson, "language": language},
        )
    assert response.status_code == 200
    return response.json()


def test_wrong_understanding_answer_reteaches_same_lesson_more_simply():
    _reset_state()
    session = client.post("/api/classroom/session", json={"class_level": "JSS1"}).json()
    lesson = "To add 2 and 2, combine the two groups. The answer is 4."
    check = _start_check(session, lesson)

    with patch.object(classroom_api, "simplify_tutor_text", return_value="Put 2 counters beside 2 more counters. Count all 4.") as simplify:
        marked = client.post(
            "/api/classroom/understanding/answer",
            json={"session_token": session["session_token"], "check_id": check["check_id"], "choice_index": 0},
        )

    assert marked.status_code == 200
    body = marked.json()
    assert body["correct"] is False
    assert "Let's try it another way:" in body["feedback"]
    assert "Put 2 counters beside 2 more counters. Count all 4." in body["feedback"]
    simplify.assert_called_once_with(lesson, "English", "JSS1")


def test_correct_understanding_answer_does_not_call_reteach():
    _reset_state()
    session = client.post("/api/classroom/session", json={"class_level": "JSS2"}).json()
    check = _start_check(session, "Two plus two equals four.")

    with patch.object(classroom_api, "simplify_tutor_text") as simplify:
        marked = client.post(
            "/api/classroom/understanding/answer",
            json={"session_token": session["session_token"], "check_id": check["check_id"], "choice_index": 1},
        )

    assert marked.status_code == 200
    assert marked.json() == {
        "correct": True,
        "correct_index": 1,
        "feedback": "Add the two values to get 4.",
    }
    simplify.assert_not_called()


def test_reteach_failure_keeps_original_feedback_and_returns_successfully():
    _reset_state()
    session = client.post("/api/classroom/session", json={"class_level": "JSS3"}).json()
    check = _start_check(session, "Two plus two equals four.")

    with patch.object(classroom_api, "simplify_tutor_text", side_effect=RuntimeError("provider unavailable")):
        marked = client.post(
            "/api/classroom/understanding/answer",
            json={"session_token": session["session_token"], "check_id": check["check_id"], "choice_index": 2},
        )

    assert marked.status_code == 200
    assert marked.json()["feedback"] == "Add the two values to get 4."


def test_reteach_is_cached_for_repeat_submission_of_same_check():
    _reset_state()
    session = client.post("/api/classroom/session", json={"class_level": "JSS2"}).json()
    check = _start_check(session, "Two plus two equals four.")

    with patch.object(classroom_api, "simplify_tutor_text", return_value="Count 2, then count 2 more: 4.") as simplify:
        for choice in (0, 2):
            marked = client.post(
                "/api/classroom/understanding/answer",
                json={"session_token": session["session_token"], "check_id": check["check_id"], "choice_index": choice},
            )
            assert marked.status_code == 200
            assert "Count 2, then count 2 more: 4." in marked.json()["feedback"]

    simplify.assert_called_once()
