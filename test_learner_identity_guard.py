from pathlib import Path


SCRIPT = Path("classroom/learner_identity_guard.js").read_text(encoding="utf-8")
LOADER = Path("classroom/daily_guidance_fix.js").read_text(encoding="utf-8")


def test_versioned_identity_guard_loader_is_present():
    assert "/classroom/learner_identity_guard.js?v=20260915-learner-isolation1" in LOADER
    assert "data-learner-identity-guard" in LOADER


def test_classroom_fetches_are_owned_by_session_generation():
    assert "let generation = 0" in SCRIPT
    assert "ownerGeneration = generation" in SCRIPT
    assert "ownerGeneration !== generation" in SCRIPT
    assert "staleRequestError" in SCRIPT
    assert "AbortError" in SCRIPT


def test_change_learner_aborts_owned_requests_before_boundary():
    section = SCRIPT.split("changeLearner.addEventListener('click', () => {", 1)[1]
    assert "betweenLearners = true" in section
    assert "cancelOwnedRequests()" in section
    assert "record.controller.abort()" in SCRIPT


def test_streamed_teacher_speech_keeps_existing_audio_controller():
    assert "path === '/api/classroom/speech'" in SCRIPT
    assert "return nativeFetch(input, init)" in SCRIPT
    assert "Teacher speech already has its own AbortController" in SCRIPT


def test_stale_response_body_cannot_be_consumed_after_identity_change():
    assert "wrapResponse(response, ownerGeneration, record)" in SCRIPT
    assert "bodyMethods = new Set(['json', 'text', 'blob', 'arrayBuffer', 'formData'])" in SCRIPT
    assert "assertRequestOwner(ownerGeneration)" in SCRIPT


def test_transient_chat_and_canvas_are_cleared():
    assert "messages.replaceChildren()" in SCRIPT
    assert "canvasAnswer.replaceChildren()" in SCRIPT
    assert "problemPreview.removeAttribute('src')" in SCRIPT
    assert "backToWhiteboard.classList.add('hidden')" in SCRIPT
    assert "lessonDirector.classList.add('hidden')" in SCRIPT


def test_transient_learning_objects_are_cleared():
    for fragment in (
        "currentPractice = null",
        "currentPracticeSummary = null",
        "currentProgress = null",
        "currentRevision = null",
        "currentLesson = null",
        "lessonInterruption = null",
        "lessonHistory.length = 0",
        "understandingCheckId = null",
        "currentTeacherDashboard = null",
        "pendingChatRecovery = null",
    ):
        assert fragment in SCRIPT


def test_previous_pending_chat_is_removed_but_durable_local_storage_is_not_erased():
    assert "sessionStorage.removeItem('roboTeacherPendingChat')" in SCRIPT
    assert "localStorage.clear" not in SCRIPT
    assert "localStorage.removeItem" not in SCRIPT
    assert "roboTeacherWhiteboardDraft" not in SCRIPT


def test_stale_handlers_cannot_reveal_previous_session_between_learners():
    assert "wrapBoundaryAwareFunction('addMessage'" in SCRIPT
    assert "wrapBoundaryAwareFunction('showCanvasAnswer')" in SCRIPT
    assert "wrapBoundaryAwareFunction('keepTeachingCanvasVisible')" in SCRIPT
    assert "wrapBoundaryAwareFunction('startLessonDirector')" in SCRIPT


def test_new_start_resume_or_teacher_entry_opens_a_fresh_request_generation():
    assert "startLearning.addEventListener('click', beginFreshBoundary, true)" in SCRIPT
    assert "resumeLearning.addEventListener('click', beginFreshBoundary, true)" in SCRIPT
    assert "openTeacherDashboard.addEventListener('click', beginFreshBoundary, true)" in SCRIPT
    assert "betweenLearners = false" in SCRIPT


def test_cleanup_runs_again_after_existing_change_learner_handler_finishes():
    assert "queueMicrotask(clearTransientState)" in SCRIPT
    assert "setTimeout(clearTransientState, 80)" in SCRIPT
