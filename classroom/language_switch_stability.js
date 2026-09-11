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
  if (!languageSelect || !teacherPanelEl || !teacherVoiceStatusEl || !readAnswerEl || !canvasStatusEl || !canvasAnswerEl) return;

  let switching = false;
  let resumeNarration = false;
  let restartedNarrationSeen = false;
  let unlockTimer = 0;
  let resumeTimer = 0;
  let retryTimer = 0;

  function voiceIsActiveOrPreparing() {
    const status = teacherVoiceStatusEl.textContent || '';
    const button = readAnswerEl.textContent || '';
    return teacherPanelEl.classList.contains('speaking') ||
      teacherPanelEl.classList.contains('paused') ||
      /preparing|teaching|speaking/i.test(status) ||
      /preparing|pause|continue/i.test(button);
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
    if (voiceIsActiveOrPreparing()) {
      restartedNarrationSeen = true;
      return;
    }

    const text = narrationText();
    if (!text) return;

    // app.js normally restarts narration itself after translation. This is a
    // defensive fallback for browsers where that async restart is lost after
    // the language-change event has completed.
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

    restartedNarrationSeen = true;
  }

  function scheduleNarrationResume() {
    clearResumeTimers();
    resumeTimer = setTimeout(() => {
      resumeTimer = 0;
      forceNarrationResume();
    }, 350);
    retryTimer = setTimeout(() => {
      retryTimer = 0;
      if (resumeNarration && !voiceIsActiveOrPreparing()) forceNarrationResume();
    }, 1800);
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
    if (voiceIsActiveOrPreparing()) {
      restartedNarrationSeen = true;
      return;
    }
    if (restartedNarrationSeen) {
      resumeNarration = false;
      restartedNarrationSeen = false;
      clearResumeTimers();
    }
  }

  // Capture before app.js handles the change so we preserve the fact that the
  // learner was already listening before app.js stops the old language stream.
  document.addEventListener('change', event => {
    if (event.target !== languageSelect) return;

    const keepReading = resumeNarration || voiceIsActiveOrPreparing();
    resumeNarration = keepReading;
    restartedNarrationSeen = false;
    clearResumeTimers();

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
})();
