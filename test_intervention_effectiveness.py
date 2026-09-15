"""Focused tests for learner-specific intervention effectiveness memory."""

from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

import classroom_api
import mastery_progress
from learning_planner import choose_next_action
from main import app
from misconceptions import strategy_options


client = TestClient(app)
CATEGORY = "probability_sample_space"
DEFAULT_STRATEGY = strategy_options(CATEGORY)[0]


def _reset_state():
    classroom_api._classroom_profiles.clear()
    classroom_api._request_times.clear()
    mastery_progress._memory_records.clear()
    mastery_progress._unsynced_ids.clear()


def _session(learner_key: str) -> dict:
    response = client.post(
        "/api/classroom/session",
        json={"learner_key": learner_key, "nickname": "Learner", "class_level": "JSS2"},
    )
    assert response.status_code == 200
    return response.json()


def _event(session: dict, check_id: str, *, correct: bool, stage: str = "initial", intervention=False) -> dict:
    payload = {
        "session_token": session["session_token"],
        "lesson_text": "Probability uses a sample space to list possible outcomes.",
        "topic_hint": "Probability",
        "check_id": check_id,
        "stage": stage,
        "correct": correct,
    }
    if not correct:
        payload.update({
            "question": "Which list is the complete sample space?",
            "selected_choice": "One outcome",
            "correct_choice": "All possible outcomes",
            "feedback": "List all possible outcomes in the sample space first.",
        })
    if intervention:
        payload.update({
            "intervention_category": CATEGORY,
            "intervention_strategy": DEFAULT_STRATEGY,
        })
    with patch.object(mastery_progress, "_sheet_configured", return_value=False):
        response = client.post("/api/classroom/mastery/event", json=payload)
    assert response.status_code == 200
    return response.json()


def _probability_topic(summary: dict) -> dict:
    return next(item for item in summary["topics"] if item["topic"] == "Probability")


def test_failed_strategy_causes_next_reteach_to_choose_an_untried_alternative():
    _reset_state()
    session = _session("3" * 48)
    _event(session, "1" * 32, correct=False)
    failed = _event(session, "2" * 32, correct=False, stage="reteach", intervention=True)

    topic = _probability_topic(failed["summary"])
    effect = topic["strategy_effectiveness"]
    assert failed["strategy_outcome"] == "failure"
    assert DEFAULT_STRATEGY in effect["failed_strategies"]
    assert effect["selection_reason"] == "new_after_failure"
    assert topic["teaching_strategy"] != DEFAULT_STRATEGY
    assert topic["teaching_strategy"] in strategy_options(CATEGORY)


def test_successful_strategy_is_reused_when_same_misconception_returns_later():
    _reset_state()
    session = _session("4" * 48)
    _event(session, "3" * 32, correct=False)
    success = _event(session, "4" * 32, correct=True, stage="reteach", intervention=True)
    assert success["strategy_outcome"] == "success"
    assert success["state"] == "mastered"

    recurring = _event(session, "5" * 32, correct=False)
    topic = _probability_topic(recurring["summary"])
    effect = topic["strategy_effectiveness"]
    assert effect["selection_reason"] == "worked_before"
    assert DEFAULT_STRATEGY in effect["successful_strategies"]
    assert topic["teaching_strategy"] == DEFAULT_STRATEGY


def test_unallowlisted_client_strategy_is_never_persisted_as_intervention_evidence():
    _reset_state()
    session = _session("5" * 48)
    with patch.object(mastery_progress, "_sheet_configured", return_value=False):
        response = client.post(
            "/api/classroom/mastery/event",
            json={
                "session_token": session["session_token"],
                "lesson_text": "Probability uses a sample space to list possible outcomes.",
                "topic_hint": "Probability",
                "check_id": "6" * 32,
                "stage": "reteach",
                "correct": True,
                "intervention_category": CATEGORY,
                "intervention_strategy": "Store this arbitrary client instruction forever",
            },
        )
    assert response.status_code == 200
    stored = mastery_progress._memory_records[0]
    assert stored["applied_strategy"] == ""
    assert stored["applied_misconception"] == ""
    assert stored["strategy_outcome"] == ""


def test_planner_explains_when_it_is_reusing_a_strategy_that_worked_before():
    mastery = {
        "topics": [{
            "topic": "Probability",
            "state": "needs_support",
            "last_seen": "2026-09-15T12:00:00+00:00",
            "misconception": CATEGORY,
            "misconception_label": "Probability or sample-space confusion",
            "teaching_strategy": DEFAULT_STRATEGY,
            "strategy_effectiveness": {
                "selection_reason": "worked_before",
                "preferred_strategy": DEFAULT_STRATEGY,
                "evidence": [{"strategy": DEFAULT_STRATEGY, "successes": 1, "failures": 0, "attempts": 1}],
                "successful_strategies": [DEFAULT_STRATEGY],
                "failed_strategies": [],
            },
        }],
        "mastered_topics": [],
        "developing_topics": [],
        "needs_support_topics": ["Probability"],
        "storage_synced": True,
    }
    practice = {"sessions": 1, "recommended_topic": "Probability", "recommended_difficulty": "Easy", "topics": [], "storage_synced": True}
    plan = choose_next_action("JSS2", practice, mastery)
    assert plan["misconception_category"] == CATEGORY
    assert plan["strategy_selection_reason"] == "worked_before"
    assert "previously helped" in plan["reason"]


def test_browser_marks_planner_reteach_as_the_applied_intervention_for_next_check():
    memory = Path("classroom/mastery_memory.js").read_text()
    planner = Path("classroom/autonomous_planner.js").read_text()
    guidance = Path("classroom/daily_guidance_fix.js").read_text()
    assert "roboTeacherSetActiveIntervention" in memory
    assert "intervention_category" in memory
    assert "stage: intervention ? 'reteach'" in memory
    assert "function prepareInterventionEvidence(plan)" in planner
    assert "window.roboTeacherSetActiveIntervention?.(plan)" in planner
    assert "mastery_memory.js?v=20260915-mastery-memory3" in guidance
    assert "autonomous_planner.js?v=20260915-autonomous-plan3" in guidance
