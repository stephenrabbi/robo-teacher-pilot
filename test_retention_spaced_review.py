"""Regression tests for retention-aware spaced review scheduling."""

import datetime
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

import classroom_api
import mastery_api
import mastery_progress
import retention_progress
from learning_planner import choose_next_action
from main import app


client = TestClient(app)


def _reset_state():
    classroom_api._classroom_profiles.clear()
    classroom_api._request_times.clear()
    mastery_progress._memory_records.clear()
    mastery_progress._unsynced_ids.clear()
    retention_progress.reset_for_tests()


def _session(learner_key: str = "a" * 48, class_level: str = "JSS2") -> dict:
    response = client.post(
        "/api/classroom/session",
        json={"learner_key": learner_key, "nickname": "Retention Learner", "class_level": class_level},
    )
    assert response.status_code == 200
    return response.json()


def _practice():
    return {
        "sessions": 2,
        "recommended_topic": "Probability",
        "recommended_difficulty": "Easy",
        "topics": [],
        "storage_synced": True,
    }


def _mastery(state="mastered", checks=3):
    return {
        "topics": [{
            "topic": "Probability",
            "state": state,
            "last_seen": "2026-09-15T12:00:00+00:00",
            "checks": checks,
        }],
        "mastered_topics": ["Probability"] if state == "mastered" else [],
        "developing_topics": ["Probability"] if state == "developing" else [],
        "needs_support_topics": ["Probability"] if state == "needs_support" else [],
        "storage_synced": True,
    }


def test_interval_progression_extends_after_success_and_resets_after_lapse():
    _reset_state()
    first = retention_progress.schedule_after_mastery(
        "mastery-1", "learner-1", "RT-001", "JSS2", "Probability"
    )
    assert first["interval_days"] == 2
    assert first["outcome"] == "scheduled"

    retained = retention_progress.record_review_result(
        "review-1", "learner-1", "RT-001", "JSS2", "Probability", True
    )
    assert retained["interval_days"] == 7
    assert retained["outcome"] == "retained"

    lapse = retention_progress.record_review_result(
        "review-2", "learner-1", "RT-001", "JSS2", "Probability", False
    )
    assert lapse["interval_days"] == 1
    assert lapse["outcome"] == "lapse"

    recovered = retention_progress.schedule_after_mastery(
        "mastery-2", "learner-1", "RT-001", "JSS2", "Probability"
    )
    assert recovered["interval_days"] == 1
    assert recovered["outcome"] == "recovered"


def test_due_summary_uses_structured_schedule_only():
    _reset_state()
    scheduled = retention_progress.schedule_after_mastery(
        "mastery-3", "learner-2", "RT-002", "JSS2", "Probability"
    )
    due_at = datetime.datetime.fromisoformat(scheduled["next_review_at"])
    with patch.object(retention_progress, "_sheet_configured", return_value=False), patch.object(
        mastery_progress, "_sheet_configured", return_value=False
    ):
        summary = retention_progress.learner_retention_summary(
            "learner-2", "JSS2", now=due_at + datetime.timedelta(minutes=1)
        )
    assert summary["due_topics"] == ["Probability"]
    row = summary["topics"][0]
    assert row["interval_days"] == 2
    assert row["due"] is True


def test_confirmed_mastery_starts_two_day_schedule_via_api():
    _reset_state()
    session = _session("b" * 48)
    with patch.object(mastery_progress, "_sheet_configured", return_value=False), patch.object(
        retention_progress, "_sheet_configured", return_value=False
    ), patch.object(mastery_api, "is_review_due", return_value=False):
        response = client.post(
            "/api/classroom/mastery/event",
            json={
                "session_token": session["session_token"],
                "lesson_text": "Probability is the chance that an outcome will happen.",
                "topic_hint": "Probability",
                "check_id": "1" * 32,
                "stage": "reteach",
                "correct": True,
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["state"] == "mastered"
    assert body["retention_outcome"] == "scheduled"
    assert body["retention_interval_days"] == 2


def test_successful_due_review_remains_mastered_and_extends_interval():
    _reset_state()
    session = _session("c" * 48)
    with patch.object(mastery_progress, "_sheet_configured", return_value=False), patch.object(
        retention_progress, "_sheet_configured", return_value=False
    ), patch.object(mastery_api, "is_review_due", return_value=True):
        response = client.post(
            "/api/classroom/mastery/event",
            json={
                "session_token": session["session_token"],
                "lesson_text": "Quick retrieval review of Probability.",
                "topic_hint": "Probability",
                "check_id": "2" * 32,
                "stage": "initial",
                "correct": True,
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["retention_review"] is True
    assert body["retention_outcome"] == "retained"
    assert body["retention_interval_days"] == 7
    assert body["state"] == "mastered"
    assert "Probability" in body["summary"]["mastered_topics"]


def test_failed_due_review_becomes_retention_lapse_without_storing_answer_content():
    _reset_state()
    session = _session("d" * 48)
    unique_question = "PRIVATE-REVIEW-QUESTION-84927"
    with patch.object(mastery_progress, "_sheet_configured", return_value=False), patch.object(
        retention_progress, "_sheet_configured", return_value=False
    ), patch.object(mastery_api, "is_review_due", return_value=True):
        response = client.post(
            "/api/classroom/mastery/event",
            json={
                "session_token": session["session_token"],
                "lesson_text": "Quick retrieval review of Probability.",
                "topic_hint": "Probability",
                "check_id": "3" * 32,
                "stage": "initial",
                "correct": False,
                "question": unique_question,
                "selected_choice": "private wrong choice",
                "correct_choice": "private correct choice",
                "feedback": "private feedback",
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["state"] == "needs_support"
    assert body["retention_outcome"] == "lapse"
    assert body["retention_interval_days"] == 1
    assert retention_progress._memory_records
    stored = retention_progress._memory_records[-1]
    assert unique_question not in repr(stored)
    assert "question" not in stored
    assert "selected_choice" not in stored
    assert "correct_choice" not in stored
    assert "feedback" not in stored


def test_planner_prioritizes_due_retention_review_when_learning_is_stable():
    retention = {
        "topics": [{
            "topic": "Probability",
            "outcome": "retained",
            "interval_days": 7,
            "next_review_at": "2026-09-15T08:00:00+00:00",
            "due": True,
        }],
        "due_topics": ["Probability"],
        "storage_synced": True,
    }
    plan = choose_next_action("JSS2", _practice(), _mastery("mastered"), retention)
    assert plan["action"] == "review"
    assert plan["reason_code"] == "retention_review_due"
    assert plan["retention_interval_days"] == 7
    assert "success will lengthen" in plan["reason"].lower()


def test_planner_treats_failed_review_as_retention_lapse_not_generic_failure():
    retention = {
        "topics": [{
            "topic": "Probability",
            "outcome": "lapse",
            "interval_days": 1,
            "next_review_at": "2026-09-16T08:00:00+00:00",
            "due": False,
        }],
        "due_topics": [],
        "storage_synced": True,
    }
    plan = choose_next_action("JSS2", _practice(), _mastery("needs_support", checks=1), retention)
    assert plan["action"] == "reteach"
    assert plan["reason_code"] == "retention_lapse"
    assert plan["title"] == "Refresh after a retention lapse"
    assert "previously mastered" in plan["reason"]


def test_manual_and_autopilot_review_paths_open_real_understanding_checks():
    planner = Path("classroom/autonomous_planner.js").read_text(encoding="utf-8")
    autopilot = Path("classroom/autopilot_session.js").read_text(encoding="utf-8")
    assert "['mastery_check','review'].includes(plan.action)" in planner
    assert "understandingButton.click()" in planner
    assert "openUnderstandingWhenReady(before)" in autopilot
    assert "plan.action === 'review'" not in autopilot or "openUnderstandingWhenReady(before)" in autopilot


def test_retention_store_has_no_transcript_or_answer_fields():
    source = Path("retention_progress.py").read_text(encoding="utf-8")
    assert '"Lesson Text"' not in source
    assert '"Question"' not in source
    assert '"Selected Choice"' not in source
    assert '"Transcript"' not in source
    assert '"Voice"' not in source
