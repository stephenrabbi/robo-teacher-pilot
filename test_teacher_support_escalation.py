"""Regression tests for evidence-based human teacher escalation."""
from pathlib import Path

from intervention_support import topic_intervention
from learning_planner import choose_next_action


def _event(*, timestamp, stage="initial", correct=False, state="needs_support", misconception=""):
    return {
        "timestamp": timestamp,
        "stage": stage,
        "correct": correct,
        "state": state,
        "misconception": misconception,
    }


def _practice():
    return {
        "sessions": 2,
        "recommended_topic": "Probability",
        "recommended_difficulty": "Easy",
        "topics": [],
        "storage_synced": True,
    }


def _mastery(topic_rows, support):
    return {
        "topics": topic_rows,
        "mastered_topics": [],
        "developing_topics": [],
        "needs_support_topics": support,
        "storage_synced": True,
    }


def test_one_failed_reteach_only_puts_topic_on_watch():
    result = topic_intervention([
        _event(timestamp="2026-09-15T10:00:00+00:00"),
        _event(timestamp="2026-09-15T10:02:00+00:00", stage="reteach"),
    ])
    assert result["level"] == "watch"
    assert result["failed_reteaches"] == 1


def test_repeated_failed_reteaching_requires_teacher_support():
    result = topic_intervention([
        _event(timestamp="2026-09-15T10:00:00+00:00"),
        _event(timestamp="2026-09-15T10:02:00+00:00", stage="reteach"),
        _event(timestamp="2026-09-15T11:00:00+00:00"),
        _event(timestamp="2026-09-15T11:02:00+00:00", stage="reteach"),
    ])
    assert result["level"] == "teacher_support"
    assert result["failed_reteaches"] == 2
    assert "more than once" in result["reason"]


def test_later_mastery_clears_old_escalation():
    result = topic_intervention([
        _event(timestamp="2026-09-15T10:00:00+00:00"),
        _event(timestamp="2026-09-15T10:02:00+00:00", stage="reteach"),
        _event(timestamp="2026-09-15T11:00:00+00:00"),
        _event(timestamp="2026-09-15T11:02:00+00:00", stage="reteach"),
        _event(timestamp="2026-09-15T12:00:00+00:00", stage="reteach", correct=True, state="mastered"),
    ])
    assert result["level"] == "none"
    assert result["failed_reteaches"] == 0
    assert result["incorrect_checks"] == 0


def test_recurring_unresolved_misconception_can_trigger_support():
    result = topic_intervention([
        _event(timestamp="2026-09-15T10:00:00+00:00", misconception="probability_sample_space"),
        _event(timestamp="2026-09-15T10:10:00+00:00", misconception="probability_sample_space"),
        _event(timestamp="2026-09-15T10:20:00+00:00", misconception="probability_sample_space"),
    ])
    assert result["level"] == "teacher_support"
    assert result["recurring_misconception"] == "Probability or sample-space confusion"


def test_planner_stops_reteaching_when_current_topic_needs_teacher_support():
    mastery = _mastery([
        {
            "topic": "Probability",
            "state": "needs_support",
            "last_seen": "2026-09-15T12:00:00+00:00",
            "checks": 4,
            "intervention_level": "teacher_support",
            "intervention_reason": "Repeated support has not yet secured mastery.",
        }
    ], ["Probability"])
    plan = choose_next_action("JSS2", _practice(), mastery)
    assert plan["action"] == "teacher_help"
    assert plan["topic"] == "Probability"
    assert plan["teacher_support_required"] is True
    assert plan["reason_code"] == "teacher_support_required"
    assert plan["prompt"] == ""


def test_escalated_prerequisite_stops_before_retrying_harder_target():
    mastery = _mastery([
        {
            "topic": "Fractions, Ratios, Decimals & Percentages",
            "state": "needs_support",
            "last_seen": "2026-09-15T10:00:00+00:00",
            "checks": 4,
            "intervention_level": "teacher_support",
            "intervention_reason": "Repeated support has not yet secured mastery.",
        },
        {
            "topic": "Probability",
            "state": "needs_support",
            "last_seen": "2026-09-15T12:00:00+00:00",
            "checks": 2,
        },
    ], ["Fractions, Ratios, Decimals & Percentages", "Probability"])
    plan = choose_next_action("JSS2", _practice(), mastery)
    assert plan["action"] == "teacher_help"
    assert plan["topic"] == "Fractions, Ratios, Decimals & Percentages"
    assert plan["foundation_for"] == "Probability"
    assert plan["reason_code"] == "prerequisite_teacher_support_required"


def test_browser_never_auto_teaches_teacher_help_plan_and_teacher_view_surfaces_flag():
    autopilot = Path("classroom/autopilot_session.js").read_text()
    planner = Path("classroom/autonomous_planner.js").read_text()
    memory = Path("classroom/mastery_memory.js").read_text()
    assert "plan.action === 'teacher_help'" in autopilot
    assert "stopForTeacherSupport(plan)" in autopilot
    assert "Robo-Teacher has paused rather than repeating autonomous reteaching" in autopilot
    assert "plan.action==='teacher_help'" in planner
    assert "Show your Progress view to your teacher" in planner
    assert "Teacher support ·" in memory
    assert "teacher_support_count" in memory


def test_escalation_assets_are_cache_busted():
    guidance = Path("classroom/daily_guidance_fix.js").read_text()
    assert "mastery_memory.js?v=20260915-mastery-memory3" in guidance
    assert "autonomous_planner.js?v=20260915-autonomous-plan4" in guidance
    assert "autopilot_session.js?v=20260915-autopilot3" in guidance
