(() => {
  if (window.__roboTeacherLanguageSwitchStability) return;
  window.__roboTeacherLanguageSwitchStability = true;

  const languageSelect = document.getElementById('language');
  const teacherPanelEl = document.getElementById('teacherPanel');
  const teacherVoiceStatusEl = document.getElementById('teacherVoiceStatus');
  const readAnswerEl = document.getElementById('readAnswer');
  const canvasStatusEl = document.getElementById('canvasStatus');
  const canvasAnswerEl = document.getElementById('canvasAnswer');
  const learningStatusEl = document.getElementById('learningStatus');
  const questionEl = document.getElementById('question');
  if (!languageSelect || !teacherPanelEl || !teacherVoiceStatusEl || !readAnswerEl || !canvasStatusEl || !canvasAnswerEl) return;

  let switching = false;
  let resumeNarration = false;
  let focusGuard = false;
  let unlockTimer = 0;
  let resumeTimer = 0;
  let focusTimer = 0;
  let choreographyPreviousState = null;

  const nativeQuestionFocus = questionEl && typeof questionEl.focus === 'function'
    ? questionEl.focus.bind(questionEl)
    : null;

  if (questionEl && nativeQuestionFocus) {
    questionEl.focus = function focusQuestion(options) {
      if (focusGuard) return;
      return nativeQuestionFocus(options);
    };
  }

  function voiceIntentIsActive() {
    const status = teacherVoiceStatusEl.textContent || '';
    const button = readAnswerEl.textContent || '';
    return teacherPanelEl.classList.contains('speaking') ||
      teacherPanelEl.classList.contains('paused') ||
      /preparing|teaching|speaking/i.test(status) ||
      /preparing|pause|continue/i.test(button);
  }

  function narrationIsActive() {
    const button = readAnswerEl.textContent || '';
    return teacherPanelEl.classList.contains('speaking') ||
      teacherPanelEl.classList.contains('paused') ||
      (readAnswerEl.disabled && /preparing/i.test(button));
  }

  function suspendLessonChoreography() {
    try {
      if (typeof lessonChoreography === 'undefined') return;
      if (choreographyPreviousState === null) choreographyPreviousState = Boolean(lessonChoreography.enabled);
      lessonChoreography.enabled = false;
      if (lessonChoreography.timer) {
        clearTimeout(lessonChoreography.timer);
        lessonChoreography.timer = null;
      }
    } catch (_error) {
      choreographyPreviousState = null;
    }
  }

  function restoreLessonChoreography() {
    try {
      if (typeof lessonChoreography !== 'undefined' && choreographyPreviousState !== null) {
        lessonChoreography.enabled = choreographyPreviousState;
      }
    } catch (_error) {
      // Keep the learner flow usable even if the optional choreography state is unavailable.
    }
    choreographyPreviousState = null;
  }

  function narrationText() {
    try {
      if (typeof currentLesson !== 'undefined' && currentLesson?.text?.trim()) return currentLesson.text.trim();
    } catch (_error) {
      // Fall back to the visible translated step.
    }
    return canvasAnswerEl.textContent.trim();
  }

  function clearResumeTimer() {
    if (resumeTimer) {
      clearTimeout(resumeTimer);
      resumeTimer = 0;
    }
  }

  function forceNarrationResume() {
    if (!resumeNarration || switching || narrationIsActive()) return;
    const text = narrationText();
    if (!text) return;
    try {
      if (typeof speakText === 'function') void speakText(text, true, true);
      else readAnswerEl.click();
    } catch (_error) {
      readAnswerEl.click();
    }
  }

  function releaseFocusGuardSoon() {
    if (focusTimer) clearTimeout(focusTimer);
    focusTimer = setTimeout(() => {
      focusGuard = false;
      focusTimer = 0;
    }, 1200);
  }

  function finishSwitch(success) {
    switching = false;
    languageSelect.disabled = false;
    languageSelect.removeAttribute('aria-busy');
    if (unlockTimer) {
      clearTimeout(unlockTimer);
      unlockTimer = 0;
    }
    restoreLessonChoreography();

    // Keep programmatic chat focusing blocked until app.js has completely
    // finished its async language-change handler. This prevents mobile keyboards
    // from opening after a language switch.
    if (questionEl && document.activeElement === questionEl) questionEl.blur();
    releaseFocusGuardSoon();

    clearResumeTimer();
    if (success && resumeNarration) {
      resumeTimer = setTimeout(() => {
        resumeTimer = 0;
        forceNarrationResume();
        setTimeout(() => {
          if (resumeNarration && !narrationIsActive()) forceNarrationResume();
          else if (narrationIsActive()) resumeNarration = false;
        }, 1200);
      }, 300);
    } else if (!success) {
      resumeNarration = false;
    }
  }

  document.addEventListener('change', event => {
    if (event.target !== languageSelect) return;

    resumeNarration = resumeNarration || voiceIntentIsActive();
    clearResumeTimer();
    switching = true;
    focusGuard = true;
    suspendLessonChoreography();

    if (questionEl && document.activeElement === questionEl) questionEl.blur();
    languageSelect.disabled = true;
    languageSelect.setAttribute('aria-busy', 'true');

    if (unlockTimer) clearTimeout(unlockTimer);
    unlockTimer = setTimeout(() => finishSwitch(false), 12000);
  }, true);

  const switchObserver = new MutationObserver(() => {
    if (!switching) return;
    const selectedLabel = languageSelect.options[languageSelect.selectedIndex]?.text || languageSelect.value;
    const canvasStatus = canvasStatusEl.textContent || '';
    const learningStatus = learningStatusEl?.textContent || '';

    if (canvasStatus.includes(`Explanation switched to ${selectedLabel}`)) {
      finishSwitch(true);
      return;
    }

    if (/language switch needs another try/i.test(learningStatus)) finishSwitch(false);
  });

  switchObserver.observe(canvasStatusEl, { childList: true, characterData: true, subtree: true });
  if (learningStatusEl) switchObserver.observe(learningStatusEl, { childList: true, characterData: true, subtree: true });
})();
