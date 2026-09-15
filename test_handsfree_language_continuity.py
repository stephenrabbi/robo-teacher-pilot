"""Regression tests for hands-free language continuity during live switching."""

from pathlib import Path


def test_handsfree_locale_mapping_covers_all_supported_classroom_languages():
    app = Path("classroom/app.js").read_text(encoding="utf-8")
    assert "English:'en-NG'" in app
    assert "Yoruba:'yo-NG'" in app
    assert "Igbo:'ig-NG'" in app
    assert "Hausa:'ha-NG'" in app
    assert "handsFree.recognition.lang=handsFreeLanguage()" in app


def test_language_guard_loads_handsfree_continuity_layer():
    guard = Path("classroom/language_switch_guard_v7.js").read_text(encoding="utf-8")
    assert "handsfree_language_continuity.js?v=20260915-handsfree-language1" in guard
    assert "data-handsfree-language-continuity" in guard


def test_live_language_switch_performs_controlled_recognition_restart():
    script = Path("classroom/handsfree_language_continuity.js").read_text(encoding="utf-8")
    assert "language.addEventListener('change', restartHandsFreeInSelectedLanguage)" in script
    assert "state.processing = true" in script
    assert "recognition.addEventListener('end', restart, {once: true})" in script
    assert "recognition.stop()" in script
    assert "recognition.lang = handsFreeLanguage()" in script
    assert "startHandsFreeListening()" in script
    assert "fallbackTimer = setTimeout(restart, 1200)" in script


def test_switch_clears_old_language_partial_phrase_and_confirmation_state():
    script = Path("classroom/handsfree_language_continuity.js").read_text(encoding="utf-8")
    assert "clearHandsFreePhraseBuffer()" in script
    assert "handsFree.pending = ''" in script
    assert "handsFree.armedUntil = 0" in script
    assert "handsFree.lastPhrase = ''" in script
    assert "handsFree.lastAt = 0" in script


def test_switch_does_not_interrupt_a_question_already_being_processed():
    script = Path("classroom/handsfree_language_continuity.js").read_text(encoding="utf-8")
    assert "if (!state.enabled || state.processing || !state.recognition)" in script
    assert "do not interrupt that request" in script


def test_language_continuity_adds_no_new_voice_or_answer_persistence():
    script = Path("classroom/handsfree_language_continuity.js").read_text(encoding="utf-8")
    assert "localStorage" not in script
    assert "sessionStorage" not in script
    assert "indexedDB" not in script
    assert "transcript" not in script.lower()
