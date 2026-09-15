"""Focused tests for misconception-aware mastery memory."""

from unittest.mock import patch

from fastapi.testclient import TestClient

import classroom_api
import mastery_progress
from main import app
from misconceptions import classify_misconception


client = TestClient(app)


def _reset_state():
    classroom_api._classroom_profiles.clear()
    classroom_api._request_times.clear()
    mastery_progress._memory_records.clear()
    mastery_progress._unsynced_ids.clear()


def _session(learner_key: str = "f" * 48, class_level: str = "JSS2") -> dict:
    response = client.post(
        "/api/classroom/session",
        json={"learner_key": learner_key, "nickname": "Learner", "class_level": class_level},
    )
    assert response.status_code == 200
    return response.json()


def _event(session: dict, check_id: str, *, correct: bool, stage: str = "initial", **extra) -> dict:
    payload = {
        "session_token": session["session_token"],
        "lesson_text": extra.pop("lesson_text", "Probability uses a sample space to list possible outcomes."),
        "topic_hint": extra.pop("topic_hint", "Probability"),
        "check_id": check_id,
        "stage": stage,
        "correct": correct,
        **extra,
    }
    with patch.object(mastery_progress, "_sheet_configured", return_value=False):
        response = client.post("/api/classroom/mastery/event", json=payload)
    assert response.status_code == 200
    return response.json()


def test_probability_error_is_classified_as_sample_space_confusion():
    result = classify_misconception(
        "Probability",
        question="Which list is the complete sample space for one coin toss?",
        selected_choice="Heads only",
        correct_choice="Heads and Tails",
        feedback="List every possible outcome in the sample space before counting favourable outcomes.",
    )
    assert result["category"] == "probability_sample_space"
    assert "sample-space" in result["label"].lower()


def test_wrong_check_persists_only_compact_diagnosis_not_transient_answer_text():
    _reset_state()
    session = _session()
    secret_question = "PRIVATE-QUESTION-92817 sample space question"
    secret_selected = "PRIVATE-WRONG-CHOICE-331"
    secret_correct = "PRIVATE-CORRECT-CHOICE-442"
    secret_feedback = "PRIVATE-FEEDBACK-553 list the sample space and possible outcomes"
    result = _event(
        session,
        "a" * 32,
        correct=False,
        question=secret_question,
        selected_choice=secret_selected,
        correct_choice=secret_correct,
        feedback=secret_feedback,
    )
    assert result["stored"] is True
    assert result["misconception"]["category"] == "probability_sample_space"
    stored = mastery_progress._memory_records[0]
    assert stored["misconception"] == "probability_sample_space"
    assert stored["teaching_strategy"]
    for raw_key in ("question", "selected_choice", "correct_choice", "feedback", "lesson_text"):
        assert raw_key not in stored
    rendered = repr(stored)
    for secret in (secret_question, secret_selected, secret_correct, secret_feedback):
        assert secret not in rendered


def test_successful_reteach_clears_active_misconception_focus():
    _reset_state()
    session = _session(learner_key="1" * 48)
    wrong = _event(
        session,
        "b" * 32,
        correct=False,
        question="What is the sample space?",
        selected_choice="One outcome",
        correct_choice="All possible outcomes",
        feedback="List all possible outcomes in the sample space.",
    )
    assert wrong["summary"]["misconception_focus"]["category"] == "probability_sample_space"

    mastered = _event(session, "c" * 32, correct=True, stage="reteach")
    assert mastered["state"] == "mastered"
    assert mastered["summary"]["misconception_focus"] is None
    topic = next(item for item in mastered["summary"]["topics"] if item["topic"] == "Probability")
    assert topic["misconception"] is None
    assert topic["teaching_strategy"] is None


def test_teacher_summary_surfaces_only_current_misconception_and_intervention():
    _reset_state()
    session = _session(learner_key="2" * 48)
    _event(
        session,
        "d" * 32,
        correct=False,
        question="Which outcomes belong in the sample space?",
        selected_choice="Only the expected one",
        correct_choice="Every possible outcome",
        feedback="Write the complete sample space first.",
    )
    with patch.object(mastery_progress, "_sheet_configured", return_value=False):
        current = mastery_progress.teacher_summary("JSS2")
    assert current["focus_topic"] == "Probability"
    assert current["focus_misconception"] == "Probability or sample-space confusion"
    assert current["focus_teaching_strategy"]
    assert current["learners"][0]["support_misconception"] == current["focus_misconception"]

    _event(session, "e" * 32, correct=True, stage="reteach")
    with patch.object(mastery_progress, "_sheet_configured", return_value=False):
        resolved = mastery_progress.teacher_summary("JSS2")
    assert resolved["focus_topic"] is None
    assert resolved["focus_misconception"] is None
    assert resolved["focus_teaching_strategy"] is None


def test_browser_sends_transient_evidence_but_exposes_only_compact_memory():
    memory = open("classroom/mastery_memory.js", encoding="utf-8").read()
    recheck = open("classroom/mastery_recheck.js", encoding="utf-8").read()
    assert "selected_choice" in memory
    assert "correct_choice" in memory
    assert "feedback" in memory
    assert "progress.misconception_focus" in memory
    assert "support_misconception" in memory
    assert "selectedChoice" in recheck
    assert "correctChoice" in recheck
    assert "question: data.correct ? '' : questionText" in recheck
