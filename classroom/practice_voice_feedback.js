(() => {
  if (window.__roboTeacherPracticeVoiceFeedback) return;
  window.__roboTeacherPracticeVoiceFeedback = true;

  const feedback = document.getElementById('practiceFeedback');
  const readButton = document.getElementById('readAnswer');
  const canvasAnswerEl = document.getElementById('canvasAnswer');
  const teacherPanelEl = document.getElementById('teacherPanel');
  if (!feedback || !readButton || !canvasAnswerEl || !teacherPanelEl) return;

  function feedbackReady() {
    return !feedback.classList.contains('hidden') &&
      (feedback.classList.contains('correct') || feedback.classList.contains('incorrect')) &&
      Boolean((feedback.dataset.feedbackRaw || feedback.textContent || '').trim());
  }

  function feedbackText() {
    return (feedback.dataset.feedbackRaw || feedback.textContent || '').trim();
  }

  function syncReadButton() {
    if (feedbackReady()) {
      readButton.disabled = false;
      if (!teacherPanelEl.classList.contains('speaking') && !teacherPanelEl.classList.contains('paused')) {
        readButton.innerHTML = '<span>Read feedback</span>';
        readButton.setAttribute('aria-label', 'Read the current practice feedback aloud');
      }
      return;
    }

    if (!teacherPanelEl.classList.contains('speaking') && !teacherPanelEl.classList.contains('paused')) {
      readButton.disabled = !canvasAnswerEl.textContent.trim();
      readButton.innerHTML = '<span>Read answer</span>';
      readButton.setAttribute('aria-label', 'Read the current answer aloud');
    }
  }

  readButton.addEventListener('click', event => {
    if (!feedbackReady()) return;

    // While audio is already active, allow app.js to handle Pause/Continue.
    if (teacherPanelEl.classList.contains('speaking') || teacherPanelEl.classList.contains('paused')) return;

    const text = feedbackText();
    if (!text) return;

    event.preventDefault();
    event.stopImmediatePropagation();

    try {
      if (typeof speakText === 'function') {
        void speakText(text, false, true);
      }
    } catch (_error) {
      // Leave the written feedback available if voice playback cannot start.
    }
  }, true);

  const observer = new MutationObserver(syncReadButton);
  observer.observe(feedback, {
    childList: true,
    characterData: true,
    subtree: true,
    attributes: true,
    attributeFilter: ['class', 'data-feedback-raw']
  });
  observer.observe(teacherPanelEl, { attributes: true, attributeFilter: ['class'] });

  syncReadButton();
})();
