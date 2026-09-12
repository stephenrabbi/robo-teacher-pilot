(() => {
  if (window.__roboTeacherLanguageSwitchGuardV7) return;
  window.__roboTeacherLanguageSwitchGuardV7 = true;

  // Prevent the older language-switch helper from installing competing handlers.
  window.__roboTeacherLanguageSwitchStability = true;

  const language = document.getElementById('language');
  const question = document.getElementById('question');
  const understandingArea = document.getElementById('understandingArea');
  const canvasWork = document.getElementById('canvasWork');
  const canvasEmpty = document.getElementById('canvasEmpty');
  const canvasStatus = document.getElementById('canvasStatus');
  const learningStatus = document.getElementById('learningStatus');
  if (!language || !question || !canvasStatus) return;

  let active = false;
  let releaseTimer = 0;
  let timeoutTimer = 0;
  let previousReadOnly = question.readOnly;
  let previousInputMode = question.getAttribute('inputmode');
  let choreographyEnabledBeforeSwitch = null;

  const nativeQuestionFocus = typeof question.focus === 'function' ? question.focus.bind(question) : null;
  if (nativeQuestionFocus) {
    question.focus = function guardedQuestionFocus(options) {
      if (active) return;
      return nativeQuestionFocus(options);
    };
  }

  function suspendChoreography() {
    try {
      if (typeof lessonChoreography === 'undefined') return;
      if (choreographyEnabledBeforeSwitch === null) choreographyEnabledBeforeSwitch = Boolean(lessonChoreography.enabled);
      lessonChoreography.enabled = false;
      if (lessonChoreography.timer) {
        clearTimeout(lessonChoreography.timer);
        lessonChoreography.timer = null;
      }
    } catch (_error) {}
  }

  function restoreChoreography() {
    try {
      if (typeof lessonChoreography !== 'undefined' && choreographyEnabledBeforeSwitch !== null) {
        lessonChoreography.enabled = choreographyEnabledBeforeSwitch;
      }
    } catch (_error) {}
    choreographyEnabledBeforeSwitch = null;
  }

  function hideUnexpectedUnderstandingCheck() {
    if (!active || !understandingArea || understandingArea.classList.contains('hidden')) return;
    understandingArea.classList.add('hidden');
    if (canvasWork) canvasWork.classList.remove('hidden');
    if (canvasEmpty) canvasEmpty.classList.add('hidden');
    try {
      if (typeof understandingCheckId !== 'undefined') understandingCheckId = null;
      if (typeof setTeachingStageMode === 'function') setTeachingStageMode('lesson');
    } catch (_error) {}
  }

  function blockTextInputFocus() {
    previousReadOnly = question.readOnly;
    previousInputMode = question.getAttribute('inputmode');
    question.readOnly = true;
    question.setAttribute('inputmode', 'none');
    if (document.activeElement === question) question.blur();
  }

  function restoreTextInput() {
    question.readOnly = previousReadOnly;
    if (previousInputMode === null) question.removeAttribute('inputmode');
    else question.setAttribute('inputmode', previousInputMode);
  }

  function releaseGuard() {
    if (!active) return;
    active = false;
    if (releaseTimer) clearTimeout(releaseTimer);
    if (timeoutTimer) clearTimeout(timeoutTimer);
    releaseTimer = 0;
    timeoutTimer = 0;
    if (document.activeElement === question) question.blur();
    restoreTextInput();
    restoreChoreography();
  }

  function scheduleRelease(delay = 2600) {
    if (releaseTimer) clearTimeout(releaseTimer);
    releaseTimer = setTimeout(releaseGuard, delay);
  }

  document.addEventListener('focusin', event => {
    if (!active) return;
    const target = event.target;
    const isTextEntry = target === question ||
      (target instanceof HTMLElement && (target.matches('textarea, input[type="text"], input:not([type])') || target.isContentEditable));
    if (isTextEntry && typeof target.blur === 'function') target.blur();
  }, true);

  document.addEventListener('change', event => {
    if (event.target !== language) return;
    active = true;
    if (releaseTimer) clearTimeout(releaseTimer);
    if (timeoutTimer) clearTimeout(timeoutTimer);
    blockTextInputFocus();
    suspendChoreography();
    hideUnexpectedUnderstandingCheck();
    timeoutTimer = setTimeout(releaseGuard, 15000);
  }, true);

  const statusObserver = new MutationObserver(() => {
    if (!active) return;
    hideUnexpectedUnderstandingCheck();
    const selectedLabel = language.options[language.selectedIndex]?.text || language.value;
    const canvasText = canvasStatus.textContent || '';
    const learningText = learningStatus?.textContent || '';
    if (canvasText.includes(`Explanation switched to ${selectedLabel}`)) {
      // app.js still has work to finish after it changes this status, including
      // a question.focus() call. Keep the guard alive long enough to swallow it.
      scheduleRelease(3000);
    } else if (/language switch needs another try/i.test(learningText)) {
      scheduleRelease(1200);
    }
  });

  statusObserver.observe(canvasStatus, { childList: true, characterData: true, subtree: true });
  if (learningStatus) statusObserver.observe(learningStatus, { childList: true, characterData: true, subtree: true });
  if (understandingArea) {
    const understandingObserver = new MutationObserver(hideUnexpectedUnderstandingCheck);
    understandingObserver.observe(understandingArea, { attributes: true, attributeFilter: ['class'] });
  }
})();
