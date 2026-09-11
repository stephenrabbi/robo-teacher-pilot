(() => {
  const status = document.getElementById('learningStatus');
  if (!status || document.getElementById('learningStatePill')) return;

  const row = document.createElement('div');
  row.className = 'learning-state-row';

  const pill = document.createElement('span');
  pill.id = 'learningStatePill';
  pill.className = 'learning-state-pill';
  pill.setAttribute('aria-hidden', 'true');

  status.parentNode.insertBefore(row, status);
  row.append(pill, status);

  const labels = {
    ready: 'Ready',
    listening: 'Listening',
    thinking: 'Thinking',
    teaching: 'Teaching',
    paused: 'Paused',
    retry: 'Retry'
  };

  function resolveState() {
    const state = (status.dataset.state || '').toLowerCase();
    const text = (status.textContent || '').trim().toLowerCase();

    if (state === 'listening' || /\blistening\b/.test(text)) return 'listening';
    if (state === 'speaking' || /\bspeaking\b|\bteaching\b/.test(text)) return 'teaching';
    if (state === 'paused' || /\bpaused\b|waiting for internet/.test(text)) return 'paused';

    const retryText = /try again|another try|needs attention|could not|failed|unavailable|technical hiccup|connection lost/.test(text);
    if ((state === 'attention' && retryText) || retryText) return 'retry';

    if (state === 'thinking' || /preparing|working|loading|reading|switching|checking|retrying|restoring|drawing/.test(text)) return 'thinking';
    return 'ready';
  }

  function sync() {
    const state = resolveState();
    pill.dataset.state = state;
    pill.textContent = labels[state];
    row.dataset.state = state;
  }

  const observer = new MutationObserver(sync);
  observer.observe(status, {
    attributes: true,
    attributeFilter: ['data-state'],
    childList: true,
    subtree: true,
    characterData: true
  });

  const style = document.createElement('style');
  style.id = 'robo-teacher-state-feedback-style';
  style.textContent = `
    .learning-state-row {
      display: flex;
      align-items: center;
      gap: 9px;
      flex-wrap: wrap;
      min-height: 30px;
      margin-top: -8px;
      margin-bottom: 10px;
    }
    .learning-state-row .learning-status {
      margin: 0;
      color: #c8d4e6;
      font-size: 13px;
      line-height: 1.35;
    }
    .learning-state-pill {
      min-height: 26px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 999px;
      padding: 5px 10px;
      border: 1px solid #47658b;
      background: #102744;
      color: #f7f9fc;
      font-size: 12px;
      font-weight: 800;
      letter-spacing: .25px;
      white-space: nowrap;
    }
    .learning-state-pill[data-state='listening'] {
      border-color: #67a6ff;
      background: #123b6d;
    }
    .learning-state-pill[data-state='thinking'] {
      border-color: #d39a27;
      background: #493712;
      color: #fff3c4;
    }
    .learning-state-pill[data-state='teaching'] {
      border-color: #4fc394;
      background: #0d4939;
      color: #dff8ed;
    }
    .learning-state-pill[data-state='paused'] {
      border-color: #8aa0bd;
      background: #24354d;
    }
    .learning-state-pill[data-state='retry'] {
      border-color: #f4b5aa;
      background: #5b241f;
      color: #fff0ed;
    }
    @media (max-width: 600px) {
      .learning-state-row {
        gap: 7px;
        margin-top: -6px;
        margin-bottom: 8px;
      }
      .learning-state-row .learning-status {
        font-size: 12px;
      }
      .learning-state-pill {
        min-height: 25px;
        padding: 4px 9px;
      }
    }
    @media (prefers-reduced-motion: no-preference) {
      .learning-state-pill[data-state='thinking']::before,
      .learning-state-pill[data-state='listening']::before,
      .learning-state-pill[data-state='teaching']::before {
        content: '';
        width: 6px;
        height: 6px;
        margin-right: 6px;
        border-radius: 50%;
        background: currentColor;
        animation: roboTeacherStatePulse 1.25s ease-in-out infinite;
      }
      @keyframes roboTeacherStatePulse {
        0%,100% { opacity: .35; transform: scale(.85); }
        50% { opacity: 1; transform: scale(1); }
      }
    }
  `;
  document.head.appendChild(style);

  sync();
})();
