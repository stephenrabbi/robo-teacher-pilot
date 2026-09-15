"""Focused tests for the autonomous cross-session learning planner."""
from pathlib import Path

from learning_planner import choose_next_action


def _practice(*, sessions=1, recommended_topic="Probability", recommended_difficulty="Medium", topics=None):
    return {
        "sessions": sessions,
        "recommended_topic": recommended_topic,
        "recommended_difficulty": recommended_difficulty,
        "topics": topics or [],
        "storage_synced": True,
    }


def _mastery(*, topics=None, mastered=None, developing=None, support=None):
    return {
        "topics": topics or [],
        "mastered_topics": mastered or [],
        "developing_topics": developing or [],
        "needs_support_topics": support or [],
        "storage_synced": True,
    }


def test_persistent_support_has_highest_priority_even_over_old_strong_practice():
    practice = _practice(topics=[{
        "topic": "Probability", "mastery_status": "mastered", "mastery_estimate": 90,
        "evidence_questions": 15, "due_for_review": False,
    }])
    mastery = _mastery(
        topics=[{"topic": "Probability", "state": "needs_support", "last_seen": "2026-09-15T10:00:00+00:00"}],
        support=["Probability"],
    )
    plan = choose_next_action("JSS2", practice, mastery)
    assert plan["action"] == "reteach"
    assert plan["topic"] == "Probability"
    assert plan["reason_code"] == "persistent_needs_support"


def test_later_persistent_mastery_prevents_stale_practice_failure_from_reteaching_same_topic():
    practice = _practice(
        recommended_topic="Linear Graphs",
        topics=[{
            "topic": "Probability", "mastery_status": "needs_support", "mastery_estimate": 42,
            "evidence_questions": 10, "due_for_review": False,
        }],
    )
    mastery = _mastery(
        topics=[{"topic": "Probability", "state": "mastered", "last_seen": "2026-09-15T10:30:00+00:00"}],
        mastered=["Probability"],
    )
    plan = choose_next_action("JSS2", practice, mastery)
    assert plan["action"] == "advance"
    assert plan["topic"] == "Linear Graphs"


def test_due_topic_is_reviewed_before_advancing():
    practice = _practice(topics=[{
        "topic": "Standard Form", "mastery_status": "mastered", "mastery_estimate": 86,
        "evidence_questions": 20, "due_for_review": True, "days_since_practice": 45,
    }])
    plan = choose_next_action("JSS2", practice, _mastery(mastered=["Standard Form"]))
    assert plan["action"] == "review"
    assert plan["topic"] == "Standard Form"


def test_developing_understanding_gets_mastery_check_before_new_topic():
    mastery = _mastery(
        topics=[{"topic": "Probability", "state": "developing", "last_seen": "2026-09-15T10:00:00+00:00"}],
        developing=["Probability"],
    )
    plan = choose_next_action("JSS2", _practice(recommended_topic="Linear Graphs"), mastery)
    assert plan["action"] == "mastery_check"
    assert plan["topic"] == "Probability"


def test_brand_new_learner_gets_baseline_practice_not_false_welcome_back():
    plan = choose_next_action("JSS2", _practice(sessions=0, recommended_topic="Standard Form"), _mastery())
    assert plan["action"] == "practice"
    assert plan["topic"] == "Standard Form"
    assert plan["has_history"] is False


def test_browser_planner_loads_and_supports_all_next_action_paths():
    guidance = Path("classroom/daily_guidance_fix.js").read_text()
    script = Path("classroom/autonomous_planner.js").read_text()
    assert "autonomous_planner.js?v=20260915-autonomous-plan2" in guidance
    assert "data-autonomous-planner" in guidance
    assert "/api/classroom/mastery/plan" in script
    assert "ROBO-TEACHER REMEMBERS" in script
    assert "NEXT BEST ACTION" in script
    assert "plan.action==='practice'" in script
    assert "plan.action!=='mastery_check'" in script
    assert "understandingButton.click()" in script


def test_browser_planner_recalculates_after_mastery_and_practice_evidence_changes():
    script = Path("classroom/autonomous_planner.js").read_text()
    assert "async function evidenceChanged()" in script
    assert "clearPlanCache({keepReturn:true})" in script
    assert "fetchAutonomousPlan({force=false}" in script
    assert "if(data?.stored)void evidenceChanged()" in script
    assert "renderPracticeResults=function(...args)" in script
    assert "setTimeout(()=>{void evidenceChanged()},80)" in script


def test_return_card_uses_saved_mastery_to_explain_why_the_next_action_was_chosen():
    script = Path("classroom/autonomous_planner.js").read_text()
    assert "function rememberedDetail(plan)" in script
    assert "I remember you mastered" in script
    assert "still needs some work" in script
    assert "You are ready to continue with" in script
