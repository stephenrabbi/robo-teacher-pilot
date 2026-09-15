from pathlib import Path


SCRIPT = Path("classroom/whiteboard_draft_continuity.js").read_text(encoding="utf-8")
LOADER = Path("classroom/language_switch_guard_v7.js").read_text(encoding="utf-8")


def test_versioned_whiteboard_draft_loader_is_present():
    assert "/classroom/whiteboard_draft_continuity.js?v=20260915-whiteboard-draft1" in LOADER
    assert "data-whiteboard-draft-continuity" in LOADER


def test_draft_is_device_local_and_never_uploaded_by_recovery_layer():
    assert "localStorage.setItem" in SCRIPT
    assert "whiteboard.toDataURL('image/png')" in SCRIPT
    assert "fetch(" not in SCRIPT
    assert "/api/" not in SCRIPT


def test_draft_is_scoped_to_valid_learner_code_and_class():
    assert "roboTeacherWhiteboardDraft:" in SCRIPT
    assert "learnerCode.value.trim().toUpperCase()" in SCRIPT
    assert "learnerClass.value" in SCRIPT
    assert "JSS[1-3]" in SCRIPT
    assert "A-Z0-9-" in SCRIPT


def test_drafts_are_short_lived_and_size_bounded():
    assert "DRAFT_TTL_MS = 6 * 60 * 60 * 1000" in SCRIPT
    assert "MAX_DRAFT_CHARS = 900000" in SCRIPT
    assert "pruneExpiredDrafts()" in SCRIPT
    assert "Date.now() - Number(draft.savedAt) > DRAFT_TTL_MS" in SCRIPT


def test_visible_canvas_is_isolated_between_learners():
    assert "currentOwner && currentOwner !== key" in SCRIPT
    assert "clearVisibleBoard()" in SCRIPT
    assert "whiteboard.dataset.draftOwner" in SCRIPT
    assert "storageKey() !== key" in SCRIPT


def test_reload_and_navigation_preserve_unsubmitted_draft():
    assert "window.addEventListener('pagehide', saveDraftNow)" in SCRIPT
    assert "document.visibilityState === 'hidden'" in SCRIPT
    assert "pointerup" in SCRIPT
    assert "pointercancel" in SCRIPT


def test_close_and_submit_save_but_do_not_clear_draft():
    assert "closeBoardButton.addEventListener('click', saveDraftNow, true)" in SCRIPT
    assert "submitBoardButton.addEventListener('click', saveDraftNow, true)" in SCRIPT
    submit_section = SCRIPT.split("submitBoardButton.addEventListener", 1)[1].split("if (clearBoardButton)", 1)[0]
    assert "removeDraft" not in submit_section


def test_explicit_clear_removes_saved_draft():
    clear_section = SCRIPT.split("if (clearBoardButton)", 1)[1].split("if (changeLearnerButton)", 1)[0]
    assert "removeDraft()" in clear_section
    assert "saveDraftNow" not in clear_section


def test_change_learner_saves_old_draft_then_clears_live_canvas():
    section = SCRIPT.split("if (changeLearnerButton)", 1)[1].split("window.addEventListener('pagehide'", 1)[0]
    assert "saveDraftNow()" in section
    assert "clearVisibleBoard()" in section
    assert "markBoardOwner('')" in section


def test_restore_rehydrates_canvas_and_marks_it_as_inked():
    assert "context.drawImage(image, 0, 0, whiteboard.width, whiteboard.height)" in SCRIPT
    assert "boardHasInk = true" in SCRIPT
    assert "Whiteboard draft restored on this device" in SCRIPT
