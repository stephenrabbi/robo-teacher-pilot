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
  let restartedNarrationSeen = false;
  let unlockTimer = 0;
  let resumeTimer = 0;
  let retryTimer = 0;

  const nativeQuestionFocus = questionEl && typeof questionEl.focus === 'function'
    ? questionEl.focus.bind(questionEl)
    : null;

  // app.js intentionally focuses the chat box after every language change.
  // Suppress only that automatic focus while the translation switch is active;
  // normal learner taps/focus work immediately after the switch completes.
  if (questionEl && nativeQuestionFocus) {
    questionEl.focus = function focusQuestion(options) {
      if (switching) return;
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

  function narrationActuallyRestarted() {
    const button = readAnswerEl.textContent || '';
    if (teacherPanelEl.classList.contains('speaking') || teacherPanelEl.classList.contains('paused')) return true;
    return readAnswerEl.disabled && /preparing/i.test(button);
  }

  function clearResumeTimers() {
    if (resumeTimer) {
      clearTimeout(resumeTimer);
      resumeTimer = 0;
    }
    if (retryTimer) {
      clearTimeout(retryTimer);
      retryTimer = 0;
    }
  }

  function narrationText() {
    try {
      if (typeof currentLesson !== 'undefined' && currentLesson?.text?.trim()) return currentLesson.text.trim();
    } catch (_error) {
      // Fall back to the visible translated step below.
    }
    return canvasAnswerEl.textContent.trim();
  }

  function forceNarrationResume() {
    if (!resumeNarration || switching) return;
    if (narrationActuallyRestarted()) {
      restartedNarrationSeen = true;
      return;
    }

    const text = narrationText();
    if (!text) return;

    try {
      if (typeof teacherSpeechPaused !== 'undefined') teacherSpeechPaused = false;
      if (typeof speakText === 'function') {
        void speakText(text, true, true);
      } else {
        readAnswerEl.click();
      }
    } catch (_error) {
      readAnswerEl.click();
    }
  }

  function scheduleNarrationResume() {
    clearResumeTimers();
    resumeTimer = setTimeout(() => {
      resumeTimer = 0;
      forceNarrationResume();
    }, 250);
    retryTimer = setTimeout(() => {
      retryTimer = 0;
      if (resumeNarration && !narrationActuallyRestarted()) forceNarrationResume();
    }, 1500);
  }

  function unlockLanguageSelect() {
    switching = false;
    languageSelect.disabled = false;
    languageSelect.removeAttribute('aria-busy');
    if (unlockTimer) {
      clearTimeout(unlockTimer);
      unlockTimer = 0;
    }
  }

  function syncNarrationIntent() {
    if (!resumeNarration || switching) return;
    if (narrationActuallyRestarted()) {
      restartedNarrationSeen = true;
      return;
    }
    if (restartedNarrationSeen) {
      resumeNarration = false;
      restartedNarrationSeen = false;
      clearResumeTimers();
    }
  }

  document.addEventListener('change', event => {
    if (event.target !== languageSelect) return;

    const keepReading = resumeNarration || voiceIntentIsActive();
    resumeNarration = keepReading;
    restartedNarrationSeen = false;
    clearResumeTimers();

    // Dismiss any keyboard/input focus left from an earlier learner action.
    if (questionEl && document.activeElement === questionEl) questionEl.blur();

    if (keepReading && !teacherPanelEl.classList.contains('speaking')) {
      try {
        if (typeof teacherSpeechPaused !== 'undefined') teacherSpeechPaused = true;
      } catch (_error) {
        teacherPanelEl.classList.add('paused');
      }
    }

    switching = true;
    languageSelect.disabled = true;
    languageSelect.setAttribute('aria-busy', 'true');
    if (unlockTimer) clearTimeout(unlockTimer);
    unlockTimer = setTimeout(() => {
      unlockLanguageSelect();
      if (resumeNarration) scheduleNarrationResume();
    }, 12000);
  }, true);

  const switchObserver = new MutationObserver(() => {
    const selectedLabel = languageSelect.options[languageSelect.selectedIndex]?.text || languageSelect.value;
    const canvasStatus = canvasStatusEl.textContent || '';
    const learningStatus = learningStatusEl?.textContent || '';

    if (switching && canvasStatus.includes(`Explanation switched to ${selectedLabel}`)) {
      unlockLanguageSelect();
      if (resumeNarration) scheduleNarrationResume();
      return;
    }

    if (switching && /language switch needs another try/i.test(learningStatus)) {
      unlockLanguageSelect();
      resumeNarration = false;
      restartedNarrationSeen = false;
      clearResumeTimers();
      return;
    }

    syncNarrationIntent();
  });

  switchObserver.observe(canvasStatusEl, { childList: true, characterData: true, subtree: true });
  if (learningStatusEl) {
    switchObserver.observe(learningStatusEl, { childList: true, characterData: true, subtree: true });
  }
  switchObserver.observe(teacherPanelEl, { attributes: true, attributeFilter: ['class'] });
  switchObserver.observe(teacherVoiceStatusEl, { childList: true, characterData: true, subtree: true });
  switchObserver.observe(readAnswerEl, { attributes: true, attributeFilter: ['disabled'], childList: true, characterData: true, subtree: true });
})();
