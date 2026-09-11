(() => {
  const classroom = document.getElementById('classroom');
  const startLearning = document.getElementById('startLearning');
  const learnerNickname = document.getElementById('learnerNickname');
  const learnerClass = document.getElementById('learnerClass');
  const learningArea = document.querySelector('.learning-area');
  const lessonActions = document.querySelector('.lesson-actions');
  const canvas = document.getElementById('canvas');
  const messages = document.getElementById('messages');
  const composer = document.getElementById('chatForm');
  const learningStatus = document.getElementById('learningStatus');
  const dailyPlanButton = document.getElementById('dailyPlanButton');
  const chatButton = document.getElementById('chatButton');
  const practiceButton = document.getElementById('practiceButton');
  const progressButton = document.getElementById('progressButton');
  const question = document.getElementById('question');

  if (!classroom || !startLearning || !learnerNickname || !learnerClass || !learningArea || !lessonActions || !canvas || !messages || !composer || !dailyPlanButton || !chatButton || !practiceButton || !progressButton) return;
  if (document.getElementById('learnerHome')) return;

  const home = document.createElement('section');
  home.id = 'learnerHome';
  home.className = 'learner-home hidden';
  home.setAttribute('aria-labelledby', 'learnerHomeTitle');
  home.innerHTML = `
    <div class="learner-home-hero">
      <div>
        <p class="learner-home-kicker">YOUR LEARNING HOME</p>
        <h3 id="learnerHomeTitle">Welcome back</h3>
        <p id="learnerHomeClass" class="learner-home-class"></p>
      </div>
      <div class="learner-home-progress" aria-label="Today's learning progress">
        <strong id="learnerHomeProgressValue">0/3</strong>
        <span>today</span>
      </div>
    </div>
    <section class="learner-home-today" aria-labelledby="learnerHomeTodayTitle">
      <div>
        <span>TODAY'S PLAN</span>
        <strong id="learnerHomeTodayTitle">Recall → Strengthen → Discover</strong>
        <p id="learnerHomeNext">Start with a short recall activity.</p>
      </div>
      <button id="learnerHomeContinue" type="button">Continue Today's Plan →</button>
    </section>
    <div class="learner-home-quick" aria-label="Quick learning actions">
      <button id="learnerHomeChat" type="button"><strong>Ask Robo-Teacher</strong><span>Get a step-by-step explanation</span></button>
      <button id="learnerHomePractice" type="button"><strong>Practice</strong><span>Strengthen a topic with questions</span></button>
      <button id="learnerHomeProgress" type="button"><strong>My Progress</strong><span>See your learning and next step</span></button>
    </div>
  `;

  const header = learningArea.querySelector('.lesson-header');
  if (header) header.after(home); else learningArea.prepend(home);

  const homeButton = document.createElement('button');
  homeButton.id = 'learnerHomeButton';
  homeButton.type = 'button';
  homeButton.textContent = 'Home';
  homeButton.setAttribute('aria-label', 'Open learning home');
  lessonActions.insertBefore(homeButton, lessonActions.firstChild);

  const style = document.createElement('style');
  style.id = 'robo-teacher-learner-home-style';
  style.textContent = `
    .learner-home {
      width: 100%;
      align-self: stretch;
      color: #10203a;
      display: grid;
      gap: 14px;
      margin-bottom: 12px;
    }
    .learner-home-hero {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      padding: 22px;
      border: 1px solid #cfe0f2;
      border-radius: 20px;
      background: linear-gradient(135deg,#f7fbff,#eef7ff 58%,#fff7e5);
    }
    .learner-home-kicker {
      margin: 0 0 7px;
      color: #0757c9;
      font-size: 12px;
      font-weight: 850;
      letter-spacing: 1.2px;
    }
    .learner-home-hero h3 {
      margin: 0;
      color: #10203a;
      font-size: clamp(25px,3vw,36px);
      line-height: 1.12;
    }
    .learner-home-class {
      margin: 7px 0 0;
      color: #43526a;
      font-weight: 650;
    }
    .learner-home-progress {
      flex: none;
      width: 92px;
      height: 92px;
      display: grid;
      place-items: center;
      align-content: center;
      border-radius: 50%;
      border: 7px solid #b9d8ff;
      background: #fff;
      box-shadow: 0 8px 24px #10203a18;
    }
    .learner-home-progress strong { color:#0757c9; font-size:24px; line-height:1; }
    .learner-home-progress span { margin-top:4px; color:#43526a; font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:.5px; }
    .learner-home-today {
      display: grid;
      grid-template-columns: minmax(0,1fr) auto;
      gap: 18px;
      align-items: center;
      padding: 18px 20px;
      border: 1px solid #ecd9a6;
      border-left: 5px solid #d39a27;
      border-radius: 16px;
      background: #fffaf0;
    }
    .learner-home-today span { display:block; color:#765615; font-size:11px; font-weight:850; letter-spacing:1px; }
    .learner-home-today strong { display:block; margin-top:4px; color:#362b16; font-size:18px; }
    .learner-home-today p { margin:6px 0 0; color:#4d473a; line-height:1.45; }
    .learner-home-today button {
      min-height: 46px;
      border: 0;
      border-radius: 12px;
      padding: 11px 15px;
      background: #102c53;
      color: #fff;
      font-weight: 800;
      cursor: pointer;
    }
    .learner-home-quick {
      display: grid;
      grid-template-columns: repeat(3,minmax(0,1fr));
      gap: 10px;
    }
    .learner-home-quick button {
      min-height: 92px;
      display: grid;
      gap: 5px;
      align-content: center;
      text-align: left;
      border: 1px solid #cbd8e8;
      border-radius: 15px;
      padding: 15px;
      background: #fff;
      color: #10203a;
      cursor: pointer;
      box-shadow: 0 6px 18px #10203a0d;
    }
    .learner-home-quick button:hover,
    .learner-home-quick button:focus-visible { border-color:#1677ff; background:#f5f9ff; }
    .learner-home-quick strong { font-size:16px; }
    .learner-home-quick span { color:#43526a; font-size:12px; line-height:1.35; }
    #learnerHomeButton {
      min-height:44px;
      border:1px solid var(--line);
      background:#102744;
      color:#fff;
      border-radius:10px;
      padding:8px 11px;
      font-weight:800;
      cursor:pointer;
    }
    #learnerHomeButton.active { border-color:#67a6ff; box-shadow:inset 0 -3px 0 #d39a27; background:#173f76; }
    .learner-home-open #dailyCoachCard { display:none!important; }
    @media (max-width:700px) {
      .learner-home-hero { padding:17px; }
      .learner-home-progress { width:76px; height:76px; border-width:6px; }
      .learner-home-progress strong { font-size:20px; }
      .learner-home-today { grid-template-columns:1fr; gap:12px; padding:16px; }
      .learner-home-today button { width:100%; }
      .learner-home-quick { grid-template-columns:1fr; }
      .learner-home-quick button { min-height:72px; }
    }
  `;
  document.head.appendChild(style);

  const homeTitle = document.getElementById('learnerHomeTitle');
  const homeClass = document.getElementById('learnerHomeClass');
  const progressValue = document.getElementById('learnerHomeProgressValue');
  const nextCopy = document.getElementById('learnerHomeNext');
  const continueButton = document.getElementById('learnerHomeContinue');
  const chatAction = document.getElementById('learnerHomeChat');
  const practiceAction = document.getElementById('learnerHomePractice');
  const progressAction = document.getElementById('learnerHomeProgress');

  function dateKey() {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
  }

  function dailyState() {
    const nickname = learnerNickname.value.trim().toLocaleLowerCase();
    const key = `roboTeacherDailySession:${learnerClass.value}:${nickname}:${dateKey()}`;
    try {
      const state = JSON.parse(localStorage.getItem(key) || 'null') || {};
      const completed = Array.isArray(state.completed) ? state.completed.filter(item => ['revision','practice','lesson'].includes(item)) : [];
      return { completed, activeAction: state.activeAction || '' };
    } catch (_error) {
      return { completed: [], activeAction: '' };
    }
  }

  function refreshHome() {
    const nickname = learnerNickname.value.trim() || 'Learner';
    const state = dailyState();
    const done = state.completed.length;
    const sequence = ['revision','practice','lesson'];
    const next = sequence.find(item => !state.completed.includes(item));
    const labels = { revision:'Recall', practice:'Strengthen', lesson:'Discover' };

    homeTitle.textContent = `Welcome, ${nickname}`;
    homeClass.textContent = `${learnerClass.value} Mathematics · Your personalised learning space`;
    progressValue.textContent = `${done}/3`;

    if (done >= 3) {
      nextCopy.textContent = 'You completed all three learning steps today. You can review them again or ask a new question.';
      continueButton.textContent = 'View Completed Plan ✓';
    } else if (state.activeAction && !state.completed.includes(state.activeAction)) {
      nextCopy.textContent = `Continue your ${labels[state.activeAction] || 'current'} activity from where you stopped.`;
      continueButton.textContent = 'Continue Today’s Plan →';
    } else {
      nextCopy.textContent = `Next: ${labels[next] || 'Continue'} — ${done === 0 ? 'begin with a short recall activity.' : 'keep your learning momentum going.'}`;
      continueButton.textContent = done === 0 ? 'Start Today’s Plan →' : 'Continue Today’s Plan →';
    }
  }

  function clearPrimaryActive() {
    [dailyPlanButton, chatButton, practiceButton, progressButton].forEach(button => {
      button.classList.remove('active');
      button.removeAttribute('aria-current');
    });
  }

  function showHome() {
    if (classroom.classList.contains('hidden')) return;
    refreshHome();
    home.classList.remove('hidden');
    learningArea.classList.add('learner-home-open');
    canvas.classList.add('hidden');
    messages.classList.add('hidden');
    composer.classList.add('hidden');
    clearPrimaryActive();
    homeButton.classList.add('active');
    homeButton.setAttribute('aria-current','page');
    if (learningStatus) {
      learningStatus.textContent = 'Home';
      learningStatus.dataset.state = '';
    }
  }

  function leaveHome() {
    home.classList.add('hidden');
    learningArea.classList.remove('learner-home-open');
    canvas.classList.remove('hidden');
    messages.classList.remove('hidden');
    composer.classList.remove('hidden');
    homeButton.classList.remove('active');
    homeButton.removeAttribute('aria-current');
  }

  homeButton.addEventListener('click', showHome);
  startLearning.addEventListener('click', () => setTimeout(showHome, 120));

  [dailyPlanButton, chatButton, practiceButton, progressButton].forEach(button => {
    button.addEventListener('click', leaveHome);
  });

  continueButton.addEventListener('click', () => { leaveHome(); dailyPlanButton.click(); });
  chatAction.addEventListener('click', () => { leaveHome(); chatButton.click(); setTimeout(() => question?.focus(), 0); });
  practiceAction.addEventListener('click', () => { leaveHome(); practiceButton.click(); });
  progressAction.addEventListener('click', () => { leaveHome(); progressButton.click(); });
})();
