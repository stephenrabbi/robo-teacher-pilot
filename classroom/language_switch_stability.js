(() => {
  if (window.__roboTeacherLanguageSwitchStability) return;
  window.__roboTeacherLanguageSwitchStability = true;

  const languageSelect = document.getElementById('language');
  const teacherPanelEl = document.getElementById('teacherPanel');
  const teacherVoiceStatusEl = document.getElementById('teacherVoiceStatus');
  const readAnswerEl = document.getElementById('readAnswer');
  const canvasStatusEl = document.getElementById('canvasStatus');
  const learningStatusEl = document.getElementById('learningStatus');
  if (!languageSelect || !teacherPanelEl || !teacherVoiceStatusEl || !readAnswerEl || !canvasStatusEl) return;

  let switching = false;
  let resumeNarration = false;
  let restartedNarrationSeen = false;
  let unlockTimer = 0;

  function voiceIsActiveOrPreparing() {
    const status = teacherVoiceStatusEl.textContent || '';
    const button = readAnswerEl.textContent || '';
    return teacherPanelEl.classList.contains('speaking') ||
      teacherPanelEl.classList.contains('paused') ||
      /preparing|teaching|speaking/i.test(status) ||
      /preparing|pause|continue/i.test(button);
  }

  function unlockLanguageSelect() {
    switching = false;
    languageSelect.disabled = false;
    languageSelect.removeAttribute('aria-busy');
    if (unlockTimer) {
      clearTimeout(unlockTimer);
      unlockTimer = 0;
    }
    requestAnimationFrame(syncNarrationIntent);
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
    }
  }

  // Capture before app.js handles the change. If a previous language switch is
  // still preparing a replacement voice, preserve the original "keep reading"
  // intent so the next selected language also resumes narration automatically.
  document.addEventListener('change', event => {
    if (event.target !== languageSelect) return;

    const keepReading = resumeNarration || voiceIsActiveOrPreparing();
    resumeNarration = keepReading;
    restartedNarrationSeen = false;

    // app.js determines whether to resume from its paused/speaking state. During
    // the short gap between stopping the old stream and starting the translated
    // stream, keep that intent visible to the existing handler without changing
    // the learner-facing layout.
    if (keepReading && !teacherPanelEl.classList.contains('speaking')) {
      try {
        teacherSpeechPaused = true;
      } catch (_error) {
        teacherPanelEl.classList.add('paused');
      }
    }

    // Prevent overlapping translation requests from overtaking one another.
    // The control is unlocked as soon as the current translated explanation is
    // ready, so the learner can immediately switch again while the new voice is
    // speaking.
    switching = true;
    languageSelect.disabled = true;
    languageSelect.setAttribute('aria-busy', 'true');
    if (unlockTimer) clearTimeout(unlockTimer);
    unlockTimer = setTimeout(unlockLanguageSelect, 12000);
  }, true);

  const switchObserver = new MutationObserver(() => {
    if (!switching) {
      syncNarrationIntent();
      return;
    }

    const selectedLabel = languageSelect.options[languageSelect.selectedIndex]?.text || languageSelect.value;
    const canvasStatus = canvasStatusEl.textContent || '';
    const learningStatus = learningStatusEl?.textContent || '';

    if (canvasStatus.includes(`Explanation switched to ${selectedLabel}`) ||
        /language switch needs another try/i.test(learningStatus)) {
      unlockLanguageSelect();
    }
  });

  switchObserver.observe(canvasStatusEl, { childList: true, characterData: true, subtree: true });
  if (learningStatusEl) {
    switchObserver.observe(learningStatusEl, { childList: true, characterData: true, subtree: true });
  }
  switchObserver.observe(teacherPanelEl, { attributes: true, attributeFilter: ['class'] });
  switchObserver.observe(teacherVoiceStatusEl, { childList: true, characterData: true, subtree: true });
})();
