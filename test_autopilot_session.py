"""Focused regression tests for the bounded autonomous learning session."""
from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_autopilot_loader_is_versioned_and_present():
    guidance = _read("classroom/daily_guidance_fix.js")
    assert "autopilot_session.js?v=20260915-autopilot3" in guidance
    assert "data-autopilot-session" in guidance


def test_autopilot_is_bounded_and_never_auto_answers():
    script = _read("classroom/autopilot_session.js")
    assert "const MAX_SESSION_STEPS = 3" in script
    assert "const MAX_TOPIC_ACTIONS = 2" in script
    assert "understandingButton.click()" in script
    assert "practiceForm.requestSubmit" not in script
    assert "understandingForm.requestSubmit" not in script
    assert "choice_index" not in script
    assert "Autopilot has stopped rather than repeating the same topic again" in script


def test_autopilot_keeps_learner_controls_available():
    script = _read("classroom/autopilot_session.js")
    assert "Start My Lesson" in script
    assert "pauseTeacherAudio" in script
    assert "resumeTeacherAudio" in script
    assert "stopTeacherAudio" in script
    assert "language.addEventListener('change'" in script
    assert "Autopilot will continue in the selected language" in script
    assert "Learner changed, so Autopilot stopped safely" in script
    assert "Class changed, so Autopilot stopped safely" in script


def test_autopilot_waits_for_real_learning_evidence():
    script = _read("classroom/autopilot_session.js")
    assert "window.roboTeacherMasteryRecord" in script
    assert "practiceMode === 'practice'" in script
    assert "meta.stage === 'reteach'" in script
    assert "return Boolean(meta.correct)" in script
    assert "Not quite yet. Robo-Teacher is reteaching this idea once" in script


def test_planned_mastery_confirmation_is_promoted_only_inside_autopilot():
    script = _read("classroom/autopilot_session.js")
    assert "session.currentPlan?.action === 'mastery_check'" in script
    assert "const confirmed = await original({...meta, stage: 'reteach'})" in script
    assert "plannedConfirmation" in script


def test_autopilot_uses_saved_planner_endpoint_and_updates_practice_target():
    script = _read("classroom/autopilot_session.js")
    assert "/api/classroom/mastery/plan" in script
    assert "currentProgress.recommended_topic = plan.topic" in script
    assert "currentProgress.recommended_difficulty = plan.difficulty" in script
    assert "openRecommendedPractice()" in script
