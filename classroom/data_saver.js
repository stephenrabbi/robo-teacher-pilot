(() => {
  const STORAGE_KEY = 'roboTeacherDataSaver';
  const heavyActionIds = new Set(['mediaButton', 'watchStepExample', 'visualButton', 'showStepVisual']);
  const oneTimeAllowance = new Map();
  let enabled = localStorage.getItem(STORAGE_KEY) === 'on';
  let attempts = 0;

  function ensureNotice() {
    let notice = document.getElementById('dataSaverNotice');
    if (notice) return notice;
    notice = document.createElement('div');
    notice.id = 'dataSaverNotice';
    notice.className = 'data-saver-notice hidden';
    notice.setAttribute('role', 'status');
    notice.setAttribute('aria-live', 'polite');
    document.body.appendChild(notice);
    return notice;
  }

  let noticeTimer = null;
  function showNotice(message) {
    const notice = ensureNotice();
    notice.textContent = message;
    notice.classList.remove('hidden');
    clearTimeout(noticeTimer);
    noticeTimer = setTimeout(() => notice.classList.add('hidden'), 4500);
  }

  function updateButton(button) {
    button.textContent = `Data Saver: ${enabled ? 'On' : 'Off'}`;
    button.setAttribute('aria-pressed', String(enabled));
    button.classList.toggle('data-saver-active', enabled);
    document.documentElement.dataset.dataSaver = enabled ? 'on' : 'off';
  }

  function applyLazyLoading() {
    document.querySelectorAll('#mediaArea iframe, #visualArea iframe').forEach(frame => {
      frame.setAttribute('loading', 'lazy');
    });
  }

  function installToggle() {
    attempts += 1;
    const menu = document.querySelector('.class-tools-more-menu');
    if (!menu) {
      if (attempts < 50) setTimeout(installToggle, 150);
      return;
    }
    if (document.getElementById('dataSaverButton')) return;

    const button = document.createElement('button');
    button.id = 'dataSaverButton';
    button.type = 'button';
    button.setAttribute('aria-label', 'Toggle Data Saver');
    updateButton(button);

    button.addEventListener('click', () => {
      enabled = !enabled;
      localStorage.setItem(STORAGE_KEY, enabled ? 'on' : 'off');
      updateButton(button);
      applyLazyLoading();
      showNotice(enabled
        ? 'Data Saver is on. Visuals and media will ask before loading.'
        : 'Data Saver is off. Visuals and media will load normally.');
    });

    menu.appendChild(button);
    applyLazyLoading();
  }

  document.addEventListener('click', event => {
    if (!enabled) return;
    const button = event.target.closest('button');
    if (!button || !heavyActionIds.has(button.id)) return;

    const now = Date.now();
    const allowedUntil = oneTimeAllowance.get(button.id) || 0;
    if (allowedUntil > now) {
      oneTimeAllowance.delete(button.id);
      return;
    }

    event.preventDefault();
    event.stopImmediatePropagation();
    oneTimeAllowance.set(button.id, now + 7000);
    const label = button.textContent.trim() || 'this item';
    showNotice(`Data Saver is on. Tap “${label}” again to load it once.`);
  }, true);

  const style = document.createElement('style');
  style.id = 'robo-teacher-data-saver-style';
  style.textContent = `
    #dataSaverButton.data-saver-active {
      border-color: #67a6ff;
      box-shadow: inset 0 -3px 0 #d39a27;
    }
    .data-saver-notice {
      position: fixed;
      left: 50%;
      bottom: 82px;
      z-index: 80;
      transform: translateX(-50%);
      width: min(520px, calc(100vw - 28px));
      padding: 12px 15px;
      border: 1px solid #9eb9da;
      border-radius: 12px;
      background: #f7fbff;
      color: #17355e;
      font-size: 14px;
      font-weight: 750;
      line-height: 1.4;
      text-align: center;
      box-shadow: 0 12px 30px #081a3330;
    }
    .data-saver-notice.hidden { display: none !important; }
    @media (max-width: 600px) {
      .data-saver-notice { bottom: 76px; }
    }
  `;
  document.head.appendChild(style);

  document.documentElement.dataset.dataSaver = enabled ? 'on' : 'off';
  installToggle();
})();
