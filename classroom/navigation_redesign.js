(() => {
  const nav = document.querySelector('.class-tools');
  if (!nav || nav.dataset.uxNavReady === 'true') return;

  const primaryIds = ['dailyPlanButton', 'chatButton', 'practiceButton', 'progressButton'];
  const primaryButtons = primaryIds.map(id => document.getElementById(id)).filter(Boolean);
  if (primaryButtons.length !== primaryIds.length) return;

  const teacherButton = document.getElementById('teacherDashboardButton');
  if (teacherButton) {
    teacherButton.hidden = true;
    teacherButton.setAttribute('aria-hidden', 'true');
    teacherButton.tabIndex = -1;
  }

  const contextualIds = ['simplifyButton', 'visualButton', 'mediaButton', 'understandingButton'];
  const contextualButtons = contextualIds.map(id => document.getElementById(id)).filter(Boolean);
  const inputToolIds = ['uploadButton', 'cameraButton', 'whiteboardButton'];
  const inputToolButtons = inputToolIds.map(id => document.getElementById(id)).filter(Boolean);

  const secondaryButtons = Array.from(nav.querySelectorAll(':scope > button'))
    .filter(button => !primaryIds.includes(button.id) &&
      button.id !== 'teacherDashboardButton' &&
      !contextualIds.includes(button.id) &&
      !inputToolIds.includes(button.id));

  const more = document.createElement('details');
  more.className = 'class-tools-more';

  const summary = document.createElement('summary');
  summary.textContent = 'More';
  summary.setAttribute('aria-label', 'More classroom tools');

  const menu = document.createElement('div');
  menu.className = 'class-tools-more-menu';
  menu.setAttribute('aria-label', 'More classroom tools');

  const teachingCanvas = document.getElementById('canvas');
  const canvasWork = document.getElementById('canvasWork');
  const canvasAnswer = document.getElementById('canvasAnswer');
  const lessonDirector = document.getElementById('lessonDirector');

  let lessonActions = null;
  if (teachingCanvas && contextualButtons.length) {
    lessonActions = document.createElement('nav');
    lessonActions.className = 'contextual-lesson-actions hidden';
    lessonActions.setAttribute('aria-label', 'Lesson support actions');

    const label = document.createElement('span');
    label.className = 'contextual-lesson-actions-label';
    label.textContent = 'Need another way to learn this?';
    lessonActions.appendChild(label);
    contextualButtons.forEach(button => lessonActions.appendChild(button));

    const anchor = document.getElementById('canvasVoiceAvatar');
    if (anchor) teachingCanvas.insertBefore(lessonActions, anchor);
    else teachingCanvas.appendChild(lessonActions);
  }

  const composer = document.getElementById('chatForm');
  const question = document.getElementById('question');
  let inputTools = null;
  if (composer && question && inputToolButtons.length === inputToolIds.length) {
    inputTools = document.createElement('details');
    inputTools.className = 'input-tools-more';

    const inputSummary = document.createElement('summary');
    inputSummary.textContent = '+';
    inputSummary.setAttribute('aria-label', 'Add image or use whiteboard');
    inputSummary.setAttribute('title', 'Add image or use whiteboard');

    const inputMenu = document.createElement('div');
    inputMenu.className = 'input-tools-menu';
    inputMenu.setAttribute('aria-label', 'Question input tools');

    inputToolButtons.forEach(button => inputMenu.appendChild(button));
    inputTools.append(inputSummary, inputMenu);
    composer.insertBefore(inputTools, question);

    inputToolButtons.forEach(button => {
      button.addEventListener('click', () => requestAnimationFrame(() => { inputTools.open = false; }));
    });
  }

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
    .class-tools.nav-redesigned > #teacherDashboardButton {
      display: none !important;
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
    .class-tools-more > summary::-webkit-details-marker,
    .input-tools-more > summary::-webkit-details-marker { display: none; }
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
    .class-tools-more:not([open]) .class-tools-more-menu,
    .input-tools-more:not([open]) .input-tools-menu { display: none; }
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
    .contextual-lesson-actions {
      width: 100%;
      margin-top: 16px;
      padding-top: 14px;
      border-top: 1px solid #d6e1ef;
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    .contextual-lesson-actions-label {
      width: 100%;
      color: #46566d;
      font-size: 13px;
      font-weight: 800;
      margin-bottom: 2px;
    }
    .contextual-lesson-actions button {
      min-height: 42px;
      border: 1px solid #b8c4d6;
      background: #eef4fb;
      color: #10203a;
      border-radius: 10px;
      padding: 9px 12px;
      font-weight: 750;
      cursor: pointer;
    }
    .contextual-lesson-actions button:hover,
    .contextual-lesson-actions button:focus-visible {
      border-color: #1677ff;
      background: #eaf3ff;
      color: #0757c9;
    }
    .input-tools-more {
      position: relative;
      min-width: 44px;
      align-self: stretch;
    }
    .input-tools-more > summary {
      width: 44px;
      height: 100%;
      min-height: 44px;
      display: grid;
      place-items: center;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: #102744;
      color: #fff;
      font-size: 26px;
      font-weight: 500;
      line-height: 1;
      cursor: pointer;
      list-style: none;
      user-select: none;
    }
    .input-tools-more[open] > summary,
    .input-tools-more > summary:hover,
    .input-tools-more > summary:focus-visible {
      background: #17355e;
      border-color: #67a6ff;
    }
    .input-tools-menu {
      position: absolute;
      left: 0;
      bottom: calc(100% + 10px);
      z-index: 35;
      width: 190px;
      display: grid;
      gap: 7px;
      padding: 9px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: #081a33;
      box-shadow: 0 16px 40px #0008;
    }
    .input-tools-menu button {
      width: 100%;
      min-height: 44px;
      margin: 0;
      text-align: left;
      color: #e3eaf5;
      background: #102744;
      border: 1px solid #29466c;
      border-radius: 10px;
      padding: 9px 11px;
      white-space: normal;
    }
    .input-tools-menu button:hover,
    .input-tools-menu button:focus-visible {
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
      .contextual-lesson-actions {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 7px;
      }
      .contextual-lesson-actions-label { grid-column: 1 / -1; }
      .contextual-lesson-actions button {
        width: 100%;
        min-height: 44px;
        padding: 8px 9px;
        font-size: 13px;
      }
      .input-tools-menu {
        position: fixed;
        left: 10px;
        right: 10px;
        bottom: 138px;
        width: auto;
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }
      .input-tools-menu button {
        text-align: center;
        font-size: 13px;
      }
    }
    @media (max-width: 420px) {
      .class-tools-more-menu { grid-template-columns: 1fr; }
      .input-tools-menu { grid-template-columns: 1fr; }
    }
  `;
  document.head.appendChild(style);

  secondaryButtons.forEach(button => menu.appendChild(button));
  more.append(summary, menu);

  primaryButtons.forEach(button => nav.appendChild(button));
  nav.appendChild(more);
  nav.classList.add('nav-redesigned');
  nav.dataset.uxNavReady = 'true';

  function syncLessonActions() {
    if (!lessonActions || !canvasWork) return;
    const hasAnswer = Boolean(canvasAnswer?.textContent?.trim());
    const hasLesson = Boolean(lessonDirector && !lessonDirector.classList.contains('hidden'));
    const hasActiveCanvas = !canvasWork.classList.contains('hidden');
    lessonActions.classList.toggle('hidden', !(hasActiveCanvas && (hasAnswer || hasLesson)));
  }

  function syncMoreActive() {
    more.classList.toggle('has-active', secondaryButtons.some(button => button.classList.contains('active')));
  }

  secondaryButtons.forEach(button => {
    new MutationObserver(syncMoreActive).observe(button, { attributes: true, attributeFilter: ['class'] });
    button.addEventListener('click', () => requestAnimationFrame(() => { more.open = false; }));
  });
  primaryButtons.forEach(button => button.addEventListener('click', () => { more.open = false; }));

  if (canvasWork) new MutationObserver(syncLessonActions).observe(canvasWork, { attributes: true, attributeFilter: ['class'] });
  if (canvasAnswer) new MutationObserver(syncLessonActions).observe(canvasAnswer, { childList: true, subtree: true, characterData: true });
  if (lessonDirector) new MutationObserver(syncLessonActions).observe(lessonDirector, { attributes: true, attributeFilter: ['class'] });

  document.addEventListener('click', event => {
    if (more.open && !more.contains(event.target)) more.open = false;
    if (inputTools?.open && !inputTools.contains(event.target)) inputTools.open = false;
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && more.open) {
      more.open = false;
      summary.focus();
    }
    if (event.key === 'Escape' && inputTools?.open) {
      inputTools.open = false;
      inputTools.querySelector('summary')?.focus();
    }
  });

  syncMoreActive();
  syncLessonActions();
})();
