"""Static integration checks for the one-step mastery recheck browser loop."""
from pathlib import Path


def test_mastery_memory_loads_before_recheck_in_existing_enhancement_chain():
    guidance = Path("classroom/daily_guidance_fix.js").read_text()
    memory_asset = "mastery_memory.js?v=20260915-mastery-memory1"
    recheck_asset = "mastery_recheck.js?v=20260915-mastery-recheck2"
    assert memory_asset in guidance
    assert recheck_asset in guidance
    assert "data-mastery-memory" in guidance
    assert "data-mastery-recheck" in guidance
    assert "memory.addEventListener('load',loadRecheck,{once:true})" in guidance
    assert "document.head.appendChild(memory)" in guidance
    assert "if(window.roboTeacherMasteryRecord)loadRecheck()" in guidance


def test_mastery_recheck_intercepts_the_old_submit_handler_and_caps_retry_loop():
    script = Path("classroom/mastery_recheck.js").read_text()
    assert "understandingForm.addEventListener('submit'" in script
    assert "event.stopImmediatePropagation()" in script
    assert "const wasRetry = masteryRetryActive" in script
    assert "if (wasRetry)" in script
    assert "resetMasteryRetry()" in script


def test_wrong_answer_automatically_prepares_one_new_check_from_reteaching_feedback():
    script = Path("classroom/mastery_recheck.js").read_text()
    assert "fetch('/api/classroom/understanding/answer'" in script
    assert "fetch('/api/classroom/understanding/start'" in script
    assert "const retry = await prepareMasteryRetry(data.feedback)" in script
    assert "renderRetryCheck(retry)" in script
    assert "masteryRetryActive = true" in script


def test_follow_up_success_confirms_mastery_and_failure_stops_auto_retrying():
    script = Path("classroom/mastery_recheck.js").read_text()
    assert "wasRetry ? text.mastered : text.correct" in script
    assert "wasRetry ? text.masteredStatus" in script
    assert "text.needsReview" in script
    assert "text.needsReviewStatus" in script


def test_mastery_loop_has_copy_for_all_supported_classroom_languages():
    script = Path("classroom/mastery_recheck.js").read_text()
    for language in ("English", "Yoruba", "Igbo", "Hausa"):
        assert f"{language}: {{" in script
