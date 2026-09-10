(() => {
  const nav = document.querySelector('.class-tools');
  if (!nav || nav.dataset.uxNavReady === 'true') return;

  const primaryIds = ['dailyPlanButton', 'chatButton', 'practiceButton', 'progressButton'];
  const primaryButtons = primaryIds.map(id => document.getElementById(id)).filter(Boolean);
  if (primaryButtons.length !== primaryIds.length) return;

  const secondaryButtons = Array.from(nav.querySelectorAll(':scope > button'))
    .filter(button => !primaryIds.includes(button.id));

  const more = document.createElement('details');
  more.className = 'class-tools-more';

  const summary = document.createElement('summary');
  summary.textContent = 'More';
  summary.setAttribute('aria-label', 'More classroom tools');

  const menu = document.createElement('div');
  menu.className = 'class-tools-more-menu';
  menu.setAttribute('aria-label', 'More classroom tools');

  const style = document.createElement('style');
  style.id = 'robo-teacher-navigation-redesign';
  style.textContent = `
    .class-tools.nav-redesigned {
      display: grid !important;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 8px;
      overflow: visible !important;
      padding: 0;
      align-items: stretch;
    }
    .class-tools.nav-redesigned > button,
    .class-tools.nav-redesigned > .class-tools-more > summary {
      min-height: 48px;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      font-weight: 750;
      color: var(--muted);
      border: 1px solid var(--line);
      background: #102744;
      border-radius: 12px;
      padding: 10px 8px;
      cursor: pointer;
      user-select: none;
      list-style: none;
    }
    .class-tools.nav-redesigned > button.active,
    .class-tools.nav-redesigned > button[aria-current='page'],
    .class-tools.nav-redesigned > .class-tools-more.has-active > summary {
      color: #fff;
      background: #173f76;
      border-color: #67a6ff;
      box-shadow: inset 0 -3px 0 #d39a27;
    }
    .class-tools-more {
      position: relative;
      min-width: 0;
    }
    .class-tools-more > summary::-webkit-details-marker { display: none; }
    .class-tools-more > summary::after {
      content: ' ···';
      letter-spacing: 1px;
      color: #d39a27;
    }
    .class-tools-more-menu {
      position: absolute;
      right: 0;
      bottom: calc(100% + 10px);
      z-index: 30;
      width: min(430px, 86vw);
      max-height: min(62vh, 480px);
      overflow-y: auto;
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: #081a33;
      box-shadow: 0 18px 46px #0008;
    }
    .class-tools-more:not([open]) .class-tools-more-menu { display: none; }
    .class-tools-more-menu button {
      width: 100%;
      min-height: 46px;
      margin: 0;
      text-align: left;
      color: #e3eaf5;
      background: #102744;
      border: 1px solid #29466c;
      border-radius: 11px;
      padding: 10px 12px;
      white-space: normal !important;
    }
    .class-tools-more-menu button:hover,
    .class-tools-more-menu button:focus-visible {
      background: #17355e;
      color: #fff;
    }
    @media (max-width: 600px) {
      .class-tools.nav-redesigned { gap: 5px; }
      .class-tools.nav-redesigned > button,
      .class-tools.nav-redesigned > .class-tools-more > summary {
        min-height: 50px;
        padding: 8px 4px;
        font-size: 12px;
      }
      .class-tools-more-menu {
        position: fixed;
        left: 10px;
        right: 10px;
        bottom: 74px;
        width: auto;
        max-height: 54vh;
        grid-template-columns: 1fr 1fr;
        border-radius: 18px;
      }
    }
    @media (max-width: 420px) {
      .class-tools-more-menu { grid-template-columns: 1fr; }
    }
  `;
  document.head.appendChild(style);

  secondaryButtons.forEach(button => menu.appendChild(button));
  more.append(summary, menu);

  primaryButtons.forEach(button => nav.appendChild(button));
  nav.appendChild(more);
  nav.classList.add('nav-redesigned');
  nav.dataset.uxNavReady = 'true';

  function syncMoreActive() {
    more.classList.toggle('has-active', secondaryButtons.some(button => button.classList.contains('active')));
  }

  secondaryButtons.forEach(button => {
    new MutationObserver(syncMoreActive).observe(button, { attributes: true, attributeFilter: ['class'] });
    button.addEventListener('click', () => requestAnimationFrame(() => { more.open = false; }));
  });
  primaryButtons.forEach(button => button.addEventListener('click', () => { more.open = false; }));

  document.addEventListener('click', event => {
    if (more.open && !more.contains(event.target)) more.open = false;
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && more.open) {
      more.open = false;
      summary.focus();
    }
  });

  syncMoreActive();
})();
