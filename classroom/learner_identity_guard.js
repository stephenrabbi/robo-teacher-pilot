(() => {
  if (window.__roboTeacherLearnerIdentityGuard) return;
  window.__roboTeacherLearnerIdentityGuard = true;

  const changeLearner = document.getElementById('changeLearner');
  const startLearning = document.getElementById('startLearning');
  const resumeLearning = document.getElementById('resumeLearning');
  const openTeacherDashboard = document.getElementById('openTeacherDashboard');
  const messages = document.getElementById('messages');
  const canvasAnswer = document.getElementById('canvasAnswer');
  const canvasWork = document.getElementById('canvasWork');
  const canvasEmpty = document.getElementById('canvasEmpty');
  const canvasStatus = document.getElementById('canvasStatus');
  const problemPreview = document.getElementById('problemPreview');
  const backToWhiteboard = document.getElementById('backToWhiteboard');
  const lessonDirector = document.getElementById('lessonDirector');
  const lessonPauseNotice = document.getElementById('lessonPauseNotice');
  const question = document.getElementById('question');
  const readAnswer = document.getElementById('readAnswer');
  if (!changeLearner || !messages || !canvasAnswer) return;

  const nativeFetch = window.fetch.bind(window);
  const ownedRequests = new Set();
  let generation = 0;
  let betweenLearners = false;

  function staleRequestError() {
    try { return new DOMException('Learner session changed', 'AbortError'); }
    catch (_error) { const error = new Error('Learner session changed'); error.name = 'AbortError'; return error; }
  }

  function classroomRequestPath(input) {
    try {
      const raw = typeof input === 'string' || input instanceof URL ? String(input) : input?.url;
      if (!raw) return '';
      const url = new URL(raw, window.location.href);
      if (url.origin !== window.location.origin) return '';
      return url.pathname.startsWith('/api/classroom/') ? url.pathname : '';
    } catch (_error) { return ''; }
  }

  function releaseRequest(record) {
    if (!record) return;
    ownedRequests.delete(record);
    if (record.externalSignal && record.externalAbort) {
      try { record.externalSignal.removeEventListener('abort', record.externalAbort); } catch (_error) {}
    }
  }

  function assertRequestOwner(ownerGeneration) {
    if (ownerGeneration !== generation) throw staleRequestError();
  }

  function wrapResponse(response, ownerGeneration, record) {
    const bodyMethods = new Set(['json', 'text', 'blob', 'arrayBuffer', 'formData']);
    return new Proxy(response, {
      get(target, property) {
        assertRequestOwner(ownerGeneration);
        const value = Reflect.get(target, property, target);
        if (typeof value !== 'function') return value;
        if (!bodyMethods.has(property)) return value.bind(target);
        return async (...args) => {
          try {
            const result = await value.apply(target, args);
            assertRequestOwner(ownerGeneration);
            return result;
          } finally {
            releaseRequest(record);
          }
        };
      }
    });
  }

  window.fetch = function learnerOwnedFetch(input, init = {}) {
    const path = classroomRequestPath(input);
    // Teacher speech already has its own AbortController and is stopped by the
    // existing Change Learner handler. Do not interpose on its streamed body.
    if (!path || path === '/api/classroom/speech') return nativeFetch(input, init);

    const ownerGeneration = generation;
    const controller = new AbortController();
    const record = {controller, externalSignal: init?.signal || null, externalAbort: null};
    ownedRequests.add(record);

    if (record.externalSignal) {
      record.externalAbort = () => {
        try { controller.abort(record.externalSignal.reason); } catch (_error) { controller.abort(); }
      };
      if (record.externalSignal.aborted) record.externalAbort();
      else record.externalSignal.addEventListener('abort', record.externalAbort, {once: true});
    }

    return nativeFetch(input, {...init, signal: controller.signal})
      .then(response => {
        assertRequestOwner(ownerGeneration);
        return wrapResponse(response, ownerGeneration, record);
      })
      .catch(error => {
        releaseRequest(record);
        if (ownerGeneration !== generation) throw staleRequestError();
        throw error;
      });
  };

  function cancelOwnedRequests() {
    generation += 1;
    for (const record of Array.from(ownedRequests)) {
      try { record.controller.abort(); } catch (_error) {}
      releaseRequest(record);
    }
  }

  function hide(id) {
    const element = document.getElementById(id);
    if (element) element.classList.add('hidden');
  }

  function clearTransientState() {
    // Clear only transient UI/session state. Durable learner progress, mastery,
    // saved lessons, spaced review, and learner-scoped whiteboard drafts remain.
    messages.replaceChildren();
    if (question) { question.value = ''; question.placeholder = 'Ask your teacher a question…'; }
    canvasAnswer.replaceChildren();
    if (canvasStatus) canvasStatus.textContent = 'Ready';
    if (canvasWork) {
      canvasWork.classList.add('hidden');
      canvasWork.classList.remove('text-only', 'voice-avatar-visible');
    }
    if (canvasEmpty) canvasEmpty.classList.remove('hidden');
    if (problemPreview) { problemPreview.hidden = true; problemPreview.removeAttribute('src'); }
    if (backToWhiteboard) backToWhiteboard.classList.add('hidden');
    if (lessonDirector) { lessonDirector.classList.add('hidden'); lessonDirector.classList.remove('lesson-paused'); }
    if (lessonPauseNotice) lessonPauseNotice.classList.add('hidden');
    if (readAnswer) readAnswer.disabled = true;

    [
      'understandingArea', 'visualArea', 'mediaArea', 'whiteboardArea',
      'practiceArea', 'progressArea', 'dailyPlanArea', 'myLessonsArea',
      'teacherDashboard', 'learnerCodeManager', 'qaChecklist', 'revisionPanel',
      'canvasVoiceAvatar'
    ].forEach(hide);

    try { if (typeof stopLessonMedia === 'function') stopLessonMedia(); } catch (_error) {}
    try {
      if (typeof previewUrl !== 'undefined' && previewUrl) URL.revokeObjectURL(previewUrl);
      if (typeof previewUrl !== 'undefined') previewUrl = null;
    } catch (_error) {}

    try { currentPractice = null; } catch (_error) {}
    try { currentPracticeSummary = null; } catch (_error) {}
    try { practiceMode = 'practice'; } catch (_error) {}
    try { currentProgress = null; } catch (_error) {}
    try { currentRevision = null; } catch (_error) {}
    try { currentLesson = null; } catch (_error) {}
    try { lessonInterruption = null; } catch (_error) {}
    try { if (typeof lessonHistory !== 'undefined') lessonHistory.length = 0; } catch (_error) {}
    try { understandingCheckId = null; } catch (_error) {}
    try { currentTeacherDashboard = null; } catch (_error) {}
    try { pendingChatRecovery = null; } catch (_error) {}
    try { sessionStorage.removeItem('roboTeacherPendingChat'); } catch (_error) {}
  }

  function wrapBoundaryAwareFunction(name, fallback) {
    const original = window[name];
    if (typeof original !== 'function') return;
    window[name] = function guardedTransientWrite(...args) {
      if (betweenLearners) return typeof fallback === 'function' ? fallback(...args) : undefined;
      return original.apply(this, args);
    };
  }

  // Stale request error handlers sometimes try to append a friendly message or
  // reveal the Teaching Canvas. While the device is between learner identities,
  // keep those writes detached/hidden instead of leaking the previous session.
  wrapBoundaryAwareFunction('addMessage', () => document.createElement('div'));
  wrapBoundaryAwareFunction('showCanvasAnswer');
  wrapBoundaryAwareFunction('keepTeachingCanvasVisible');
  wrapBoundaryAwareFunction('startLessonDirector');

  changeLearner.addEventListener('click', () => {
    betweenLearners = true;
    cancelOwnedRequests();
  }, true);

  changeLearner.addEventListener('click', () => {
    // The app's existing handler runs first in the bubble phase; clear the
    // remaining transient lesson data immediately after it completes.
    clearTransientState();
    queueMicrotask(clearTransientState);
    setTimeout(clearTransientState, 80);
  });

  function beginFreshBoundary() {
    cancelOwnedRequests();
    clearTransientState();
    betweenLearners = false;
  }

  if (startLearning) startLearning.addEventListener('click', beginFreshBoundary, true);
  if (resumeLearning) resumeLearning.addEventListener('click', beginFreshBoundary, true);
  if (openTeacherDashboard) openTeacherDashboard.addEventListener('click', beginFreshBoundary, true);
})();
