"""Regression tests for durable, privacy-light Autopilot session resume."""
from pathlib import Path

import autopilot_progress as progress


def _offline_store(monkeypatch):
    progress.reset_for_tests()
    monkeypatch.setattr(progress, "_sheet_configured", lambda: False)


def test_interrupted_session_resumes_from_last_confirmed_step(monkeypatch):
    _offline_store(monkeypatch)
    first = progress.start_or_resume_session("learner-a", "JSS2")
    session_id = first["session"]["session_id"]
    assert first["resumed"] is False
    assert first["session"]["completed_steps"] == 0

    progress.transition_session("learner-a", "JSS2", session_id, "active", 1)
    status = progress.session_status("learner-a", "JSS2")
    assert status["resumable"] is True
    assert status["session"]["completed_steps"] == 1

    resumed = progress.start_or_resume_session("learner-a", "JSS2")
    assert resumed["resumed"] is True
    assert resumed["session"]["session_id"] == session_id
    assert resumed["session"]["completed_steps"] == 1


def test_pause_is_resumable_and_start_reactivates_same_session(monkeypatch):
    _offline_store(monkeypatch)
    first = progress.start_or_resume_session("learner-b", "JSS1")
    session_id = first["session"]["session_id"]
    paused = progress.transition_session("learner-b", "JSS1", session_id, "paused", 1)
    assert paused["session"]["status"] == "paused"

    resumed = progress.start_or_resume_session("learner-b", "JSS1")
    assert resumed["resumed"] is True
    assert resumed["session"]["session_id"] == session_id
    assert resumed["session"]["status"] == "active"
    assert resumed["session"]["completed_steps"] == 1


def test_stopped_or_completed_session_is_not_offered_for_resume(monkeypatch):
    _offline_store(monkeypatch)
    first = progress.start_or_resume_session("learner-c", "JSS3")
    session_id = first["session"]["session_id"]
    progress.transition_session("learner-c", "JSS3", session_id, "stopped", 1)
    assert progress.session_status("learner-c", "JSS3")["resumable"] is False

    second = progress.start_or_resume_session("learner-c", "JSS3")
    assert second["session"]["session_id"] != session_id
    progress.transition_session("learner-c", "JSS3", second["session"]["session_id"], "complete", 2)
    assert progress.session_status("learner-c", "JSS3")["resumable"] is False


def test_step_count_never_moves_backwards(monkeypatch):
    _offline_store(monkeypatch)
    first = progress.start_or_resume_session("learner-d", "JSS2")
    session_id = first["session"]["session_id"]
    progress.transition_session("learner-d", "JSS2", session_id, "active", 2)
    later = progress.transition_session("learner-d", "JSS2", session_id, "active", 1)
    assert later["session"]["completed_steps"] == 2


def test_session_identity_is_scoped_to_learner_and_class(monkeypatch):
    _offline_store(monkeypatch)
    first = progress.start_or_resume_session("learner-e", "JSS2")
    session_id = first["session"]["session_id"]
    assert progress.session_status("other-learner", "JSS2")["resumable"] is False
    assert progress.session_status("learner-e", "JSS1")["resumable"] is False
    try:
        progress.transition_session("other-learner", "JSS2", session_id, "active", 1)
        assert False, "cross-learner session transition should fail"
    except ValueError as exc:
        assert str(exc) == "session_not_found"


def test_durable_autopilot_rows_store_metadata_not_learning_content():
    assert progress._HEADER == [
        "Timestamp (UTC)", "Event ID", "Session ID", "Learner ID",
        "Class Level", "Status", "Completed Steps", "Sequence", "Started (UTC)",
    ]
    header_text = " ".join(progress._HEADER).lower()
    for forbidden in ("question", "answer", "transcript", "lesson text", "voice", "misconception"):
        assert forbidden not in header_text


def test_browser_detects_and_resumes_checkpoint_without_replaying_stale_content():
    script = Path("classroom/autopilot_session.js").read_text(encoding="utf-8")
    assert "/api/classroom/mastery/autopilot/session" in script
    assert "Continue My Lesson" in script
    assert "last confirmed checkpoint" in script
    assert "recalculated from your latest saved mastery" in script
    assert "sessionApi('start'" in script
    assert "checkpointSession('step')" in script
    assert "checkpointSession('pause')" in script
    assert "checkpointSession('resume')" in script
    assert "beforeunload" not in script
    assert "await advanceSession()" in script


def test_session_api_exposes_only_structured_resume_actions():
    api = Path("mastery_api.py").read_text(encoding="utf-8")
    assert "class AutopilotSessionRequest" in api
    assert 'Literal["status", "start", "step", "pause", "resume", "stop", "finish"]' in api
    assert '@router.post("/autopilot/session")' in api
    assert "persist_session_event" in api


def test_resumable_autopilot_asset_is_cache_busted():
    guidance = Path("classroom/daily_guidance_fix.js").read_text(encoding="utf-8")
    assert "autopilot_session.js?v=20260915-autopilot3" in guidance
