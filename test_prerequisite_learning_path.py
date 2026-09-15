"""Focused tests for prerequisite-aware autonomous sequencing."""
from pathlib import Path

from curriculum import CLASS_TOPICS
from learning_planner import choose_next_action
from learning_prerequisites import PREREQUISITES, direct_prerequisites, validate_prerequisite_graph


def _practice(*, sessions=1, recommended_topic="Probability", topics=None):
    return {
        "sessions": sessions,
        "recommended_topic": recommended_topic,
        "recommended_difficulty": "Medium",
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


def _row(topic, state, *, seen="2026-09-15T12:00:00+00:00", checks=1):
    return {"topic": topic, "state": state, "last_seen": seen, "checks": checks}


def test_prerequisite_graph_is_valid_and_stays_inside_each_selected_class():
    assert validate_prerequisite_graph() == []
    for class_level, graph in PREREQUISITES.items():
        allowed = set(CLASS_TOPICS[class_level])
        for target, prerequisites in graph.items():
            assert target in allowed
            assert set(prerequisites) <= allowed
            assert target not in prerequisites


def test_probability_support_backtracks_to_known_weak_fraction_foundation():
    fraction_topic = "Fractions, Ratios, Decimals & Percentages"
    mastery = _mastery(
        topics=[
            _row(fraction_topic, "needs_support", seen="2026-09-15T11:00:00+00:00", checks=2),
            _row("Probability", "needs_support", seen="2026-09-15T12:00:00+00:00", checks=2),
        ],
        support=[fraction_topic, "Probability"],
    )
    plan = choose_next_action("JSS2", _practice(), mastery)
    assert plan["action"] == "reteach"
    assert plan["topic"] == fraction_topic
    assert plan["foundation_for"] == "Probability"
    assert plan["prerequisite_state"] == "needs_support"
    assert plan["reason_code"] == "prerequisite_needs_support"
    assert "return to Probability" in plan["reason"]
    assert "prerequisite for Probability" in plan["prompt"]


def test_developing_prerequisite_gets_confirmation_before_harder_target():
    mastery = _mastery(
        topics=[
            _row("Simple Equations", "developing", seen="2026-09-15T10:00:00+00:00", checks=1),
            _row("Linear Graphs", "needs_support", seen="2026-09-15T12:00:00+00:00", checks=2),
        ],
        developing=["Simple Equations"],
        support=["Linear Graphs"],
    )
    plan = choose_next_action("JSS2", _practice(recommended_topic="Linear Graphs"), mastery)
    assert plan["action"] == "mastery_check"
    assert plan["topic"] == "Simple Equations"
    assert plan["foundation_for"] == "Linear Graphs"
    assert plan["reason_code"] == "prerequisite_not_secure"


def test_one_target_miss_does_not_guess_an_unknown_foundation_gap():
    mastery = _mastery(
        topics=[_row("Probability", "needs_support", checks=1)],
        support=["Probability"],
    )
    plan = choose_next_action("JSS2", _practice(), mastery)
    assert plan["action"] == "reteach"
    assert plan["topic"] == "Probability"
    assert plan["foundation_for"] is None
    assert plan["reason_code"] == "persistent_needs_support"


def test_repeated_target_difficulty_earns_one_unknown_prerequisite_check():
    mastery = _mastery(
        topics=[_row("Probability", "needs_support", checks=2)],
        support=["Probability"],
    )
    plan = choose_next_action("JSS2", _practice(), mastery)
    assert plan["action"] == "mastery_check"
    assert plan["topic"] == "Fractions, Ratios, Decimals & Percentages"
    assert plan["foundation_for"] == "Probability"
    assert plan["prerequisite_state"] == "unknown"
    assert plan["reason_code"] == "prerequisite_check_after_repeated_difficulty"


def test_mastered_foundation_is_not_rechecked_and_target_work_resumes():
    foundation = "Fractions, Ratios, Decimals & Percentages"
    mastery = _mastery(
        topics=[
            _row(foundation, "mastered", seen="2026-09-15T11:00:00+00:00", checks=2),
            _row("Statistics & Data Presentation", "mastered", seen="2026-09-15T11:15:00+00:00", checks=2),
            _row("Probability", "needs_support", seen="2026-09-15T12:00:00+00:00", checks=3),
        ],
        mastered=[foundation, "Statistics & Data Presentation"],
        support=["Probability"],
    )
    plan = choose_next_action("JSS2", _practice(), mastery)
    assert plan["action"] == "reteach"
    assert plan["topic"] == "Probability"
    assert plan["foundation_for"] is None


def test_practice_failure_can_backtrack_when_saved_prerequisite_evidence_is_weak():
    practice = _practice(
        recommended_topic="Commercial Arithmetic",
        topics=[
            {
                "topic": "Fractions, Ratios, Decimals & Percentages",
                "mastery_status": "needs_support",
                "mastery_estimate": 40,
                "evidence_questions": 8,
            },
            {
                "topic": "Commercial Arithmetic",
                "mastery_status": "needs_support",
                "mastery_estimate": 45,
                "evidence_questions": 8,
            },
        ],
    )
    plan = choose_next_action("JSS2", practice, _mastery())
    # The weakest topic is itself the foundation, so the planner works on it
    # directly rather than inventing another dependency.
    assert plan["topic"] == "Fractions, Ratios, Decimals & Percentages"
    assert plan["action"] == "reteach"


def test_direct_prerequisite_order_is_deterministic():
    assert direct_prerequisites("JSS2", "Probability") == (
        "Fractions, Ratios, Decimals & Percentages",
        "Statistics & Data Presentation",
    )


def test_browser_return_guidance_explains_foundation_detour():
    guidance = Path("classroom/daily_guidance_fix.js").read_text()
    script = Path("classroom/autonomous_planner.js").read_text()
    assert "autonomous_planner.js?v=20260915-autonomous-plan3" in guidance
    assert "if(plan.foundation_for)" in script
    assert "Before we continue with ${plan.foundation_for}" in script
    assert "important foundation" in script
