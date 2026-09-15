(() => {
  if (window.__roboTeacherWhiteboardDraftContinuity) return;
  window.__roboTeacherWhiteboardDraftContinuity = true;

  const whiteboard = document.getElementById('whiteboard');
  const whiteboardButton = document.getElementById('whiteboardButton');
  const backToWhiteboard = document.getElementById('backToWhiteboard');
  const clearBoardButton = document.getElementById('clearBoard');
  const closeBoardButton = document.getElementById('closeBoard');
  const submitBoardButton = document.getElementById('submitBoard');
  const changeLearnerButton = document.getElementById('changeLearner');
  const learnerCode = document.getElementById('learnerCode');
  const learnerClass = document.getElementById('learnerClass');
  if (!whiteboard || !learnerCode || !learnerClass) return;

  const PREFIX = 'roboTeacherWhiteboardDraft:';
  const DRAFT_TTL_MS = 6 * 60 * 60 * 1000;
  const MAX_DRAFT_CHARS = 900000;
  let saveTimer = 0;
  let restoreGeneration = 0;

  function learnerIdentity() {
    const code = learnerCode.value.trim().toUpperCase();
    const classLevel = learnerClass.value;
    if (!/^[A-Z0-9][A-Z0-9-]{3,23}$/.test(code) || !/^JSS[1-3]$/.test(classLevel)) return '';
    return `${classLevel}:${code}`;
  }

  function storageKey() {
    const identity = learnerIdentity();
    return identity ? `${PREFIX}${identity}` : '';
  }

  function removeDraft(key = storageKey()) {
    if (!key) return;
    try { localStorage.removeItem(key); } catch (_error) {}
  }

  function pruneExpiredDrafts() {
    const now = Date.now();
    try {
      for (let index = localStorage.length - 1; index >= 0; index -= 1) {
        const key = localStorage.key(index);
        if (!key || !key.startsWith(PREFIX)) continue;
        try {
          const draft = JSON.parse(localStorage.getItem(key) || 'null');
          if (!draft || !Number.isFinite(Number(draft.savedAt)) || now - Number(draft.savedAt) > DRAFT_TTL_MS) {
            localStorage.removeItem(key);
          }
        } catch (_error) {
          localStorage.removeItem(key);
        }
      }
    } catch (_error) {}
  }

  function hasBoardInk() {
    try { return typeof boardHasInk !== 'undefined' && Boolean(boardHasInk); }
    catch (_error) { return false; }
  }

  function markBoardOwner(key = storageKey()) {
    whiteboard.dataset.draftOwner = key;
  }

  function saveDraftNow() {
    clearTimeout(saveTimer);
    saveTimer = 0;
    const key = storageKey();
    if (!key || !hasBoardInk()) return;
    try {
      const imageData = whiteboard.toDataURL('image/png');
      if (!imageData || imageData.length > MAX_DRAFT_CHARS) return;
      const draft = {
        savedAt: Date.now(),
        width: whiteboard.width,
        height: whiteboard.height,
        imageData
      };
      localStorage.setItem(key, JSON.stringify(draft));
      markBoardOwner(key);
    } catch (_error) {
      // Draft recovery is best-effort. A full/blocked localStorage must never
      // interfere with drawing, submitting, or clearing the live whiteboard.
    }
  }

  function scheduleDraftSave(delay = 180) {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(saveDraftNow, delay);
  }

  function clearVisibleBoard() {
    try {
      if (typeof clearWhiteboard === 'function') clearWhiteboard();
      else {
        const context = whiteboard.getContext('2d');
        context.save();
        context.fillStyle = '#ffffff';
        context.fillRect(0, 0, whiteboard.width, whiteboard.height);
        context.restore();
      }
    } catch (_error) {}
  }

  function readDraft(key) {
    if (!key) return null;
    try {
      const draft = JSON.parse(localStorage.getItem(key) || 'null');
      if (!draft || typeof draft.imageData !== 'string' || !draft.imageData.startsWith('data:image/')) return null;
      if (!Number.isFinite(Number(draft.savedAt)) || Date.now() - Number(draft.savedAt) > DRAFT_TTL_MS) {
        localStorage.removeItem(key);
        return null;
      }
      return draft;
    } catch (_error) {
      removeDraft(key);
      return null;
    }
  }

  function restoreDraftForCurrentLearner() {
    const key = storageKey();
    const currentOwner = whiteboard.dataset.draftOwner || '';
    const generation = ++restoreGeneration;

    if (!key) {
      if (currentOwner) clearVisibleBoard();
      markBoardOwner('');
      return;
    }

    if (currentOwner && currentOwner !== key) clearVisibleBoard();
    markBoardOwner(key);

    const draft = readDraft(key);
    if (!draft) return;

    const image = new Image();
    image.onload = () => {
      if (generation !== restoreGeneration || storageKey() !== key) return;
      try {
        clearVisibleBoard();
        const context = whiteboard.getContext('2d');
        context.drawImage(image, 0, 0, whiteboard.width, whiteboard.height);
        if (typeof boardHasInk !== 'undefined') boardHasInk = true;
        whiteboard.dataset.ready = 'true';
        markBoardOwner(key);
        if (typeof setLearningStatus === 'function') setLearningStatus('Whiteboard draft restored on this device', 'success');
      } catch (_error) {}
    };
    image.onerror = () => removeDraft(key);
    image.src = draft.imageData;
  }

  function prepareBoardForCurrentLearner() {
    // app.js opens/initializes the board first. Run immediately afterward so
    // stale in-memory work can never cross learner identities.
    restoreDraftForCurrentLearner();
  }

  whiteboard.addEventListener('pointerdown', () => {
    const key = storageKey();
    if (key) markBoardOwner(key);
  }, true);
  whiteboard.addEventListener('pointerup', () => scheduleDraftSave(), true);
  whiteboard.addEventListener('pointercancel', () => scheduleDraftSave(), true);

  if (whiteboardButton) whiteboardButton.addEventListener('click', prepareBoardForCurrentLearner);
  if (backToWhiteboard) backToWhiteboard.addEventListener('click', prepareBoardForCurrentLearner);

  if (closeBoardButton) closeBoardButton.addEventListener('click', saveDraftNow, true);
  if (submitBoardButton) submitBoardButton.addEventListener('click', saveDraftNow, true);

  if (clearBoardButton) {
    clearBoardButton.addEventListener('click', () => {
      clearTimeout(saveTimer);
      saveTimer = 0;
      removeDraft();
      markBoardOwner(storageKey());
    });
  }

  if (changeLearnerButton) {
    changeLearnerButton.addEventListener('click', () => {
      saveDraftNow();
      ++restoreGeneration;
      setTimeout(() => {
        clearVisibleBoard();
        markBoardOwner('');
        whiteboard.dataset.ready = 'true';
      }, 0);
    }, true);
  }

  window.addEventListener('pagehide', saveDraftNow);
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') saveDraftNow();
  });

  pruneExpiredDrafts();
})();
