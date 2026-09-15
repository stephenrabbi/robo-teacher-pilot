(() => {
  if (window.__roboTeacherHandsFreeLanguageContinuity) return;
  window.__roboTeacherHandsFreeLanguageContinuity = true;

  const language = document.getElementById('language');
  const handsFreeToggle = document.getElementById('handsFreeToggle');
  const handsFreeHeard = document.getElementById('handsFreeHeard');
  if (!language) return;

  const languageLabels = {
    English: 'English',
    Yoruba: 'Yorùbá',
    Igbo: 'Igbo',
    Hausa: 'Hausa'
  };

  let restartGeneration = 0;
  let fallbackTimer = 0;

  function clearFallback() {
    if (fallbackTimer) clearTimeout(fallbackTimer);
    fallbackTimer = 0;
  }

  function resetOldLanguagePhraseState() {
    try {
      if (typeof clearHandsFreePhraseBuffer === 'function') clearHandsFreePhraseBuffer();
      if (typeof handsFree === 'undefined') return;
      handsFree.pending = '';
      handsFree.armedUntil = 0;
      handsFree.lastPhrase = '';
      handsFree.lastAt = 0;
      handsFree.bufferConfidence = 0;
    } catch (_error) {}
  }

  function showSwitchingStatus() {
    const label = languageLabels[language.value] || language.value;
    try {
      if (typeof updateHandsFreeStatus === 'function') updateHandsFreeStatus(`Switching to ${label}…`);
      if (typeof showHandsFreeHeard === 'function') showHandsFreeHeard(`Hands-free listening is switching to ${label}.`);
      else if (handsFreeHeard) {
        handsFreeHeard.textContent = `Hands-free listening is switching to ${label}.`;
        handsFreeHeard.classList.remove('hidden');
      }
    } catch (_error) {}
  }

  function restartHandsFreeInSelectedLanguage() {
    let state;
    try {
      if (typeof handsFree === 'undefined') return;
      state = handsFree;
    } catch (_error) {
      return;
    }

    // If a spoken learner question is currently being processed, app.js already
    // restarts recognition after the answer. startHandsFreeListening() will then
    // read the newly selected language, so do not interrupt that request.
    if (!state.enabled || state.processing || !state.recognition) {
      resetOldLanguagePhraseState();
      return;
    }

    const recognition = state.recognition;
    const generation = ++restartGeneration;
    clearFallback();
    resetOldLanguagePhraseState();
    showSwitchingStatus();

    // Mark this as a deliberate recognition stop. The existing `end` handler
    // will therefore not enter its exponential recovery loop while we switch
    // languages.
    state.processing = true;
    state.restartAttempts = 0;
    clearTimeout(state.restartTimer);

    let restarted = false;
    const restart = () => {
      if (restarted || generation !== restartGeneration) return;
      restarted = true;
      clearFallback();
      recognition.removeEventListener('end', restart);
      try {
        if (typeof handsFree === 'undefined' || handsFree !== state) return;
        state.processing = false;
        if (!state.enabled) return;
        if (typeof handsFreeLanguage === 'function') recognition.lang = handsFreeLanguage();
        state.restartAttempts = 0;
        if (typeof startHandsFreeListening === 'function') startHandsFreeListening();
        if (typeof updateHandsFreeStatus === 'function') updateHandsFreeStatus('Listening…');
        const label = languageLabels[language.value] || language.value;
        if (typeof showHandsFreeHeard === 'function') showHandsFreeHeard(`Hands-free is now listening in ${label}.`);
      } catch (_error) {
        state.processing = false;
        try {
          if (state.enabled && typeof scheduleHandsFreeRecovery === 'function') scheduleHandsFreeRecovery('language-switch');
        } catch (_ignored) {}
      }
    };

    recognition.addEventListener('end', restart, {once: true});
    try {
      recognition.stop();
    } catch (_error) {
      restart();
      return;
    }
    // Some mobile implementations occasionally omit `end` after a deliberate
    // stop. This bounded fallback prevents hands-free mode from remaining muted.
    fallbackTimer = setTimeout(restart, 1200);
  }

  language.addEventListener('change', restartHandsFreeInSelectedLanguage);

  // Reflect the active recognition language for screen-reader users without
  // changing the existing button design.
  language.addEventListener('change', () => {
    if (!handsFreeToggle) return;
    const label = languageLabels[language.value] || language.value;
    handsFreeToggle.dataset.listeningLanguage = label;
  });
})();
