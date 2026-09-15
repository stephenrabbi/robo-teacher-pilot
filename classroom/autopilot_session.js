(() => {
  const MAX_SESSION_STEPS = 3;
  const MAX_TOPIC_ACTIONS = 2;
  const CHECK_POLL_MS = 500;
  const CHECK_MAX_POLLS = 60;

  const session = {
    running: false,
    paused: false,
    awaitingEvidence: false,
    pendingCheck: false,
    completed: 0,
    currentPlan: null,
    topicActions: new Map(),
    checkTimer: null,
    nextTimer: null,
    masteryWrapAttempts: 0,
    practiceWrapped: false,
  };

  let card = null;
  let title = null;
  let detail = null;
  let progress = null;
  let startButton = null;
  let pauseButton = null;
  let stopButton = null;

  function profileReady() {
    return learnerNickname.value.trim().length >= 2 && /^JSS[1-3]$/.test(learnerClass.value);
  }

  function injectStyles() {
    if (document.getElementById('autopilotSessionStyles')) return;
    const style = document.createElement('style');
    style.id = 'autopilotSessionStyles';
    style.textContent = `
      .autopilot-session-card{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;margin-bottom:14px}
      .autopilot-session-copy{display:grid;gap:3px;min-width:220px;flex:1}
      .autopilot-session-copy span{font-size:.72rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase}
      .autopilot-session-copy small{line-height:1.45}
      .autopilot-session-progress{font-weight:700}
      .autopilot-session-controls{display:flex;gap:8px;flex-wrap:wrap}
      .autopilot-session-controls button{min-height:42px}
      @media (max-width:640px){.autopilot-session-controls{width:100%}.autopilot-session-controls button{flex:1}}
    `;
    document.head.appendChild(style);
  }

  function ensureCard() {
    if (card) return card;
    injectStyles();
    card = document.createElement('section');
    card.id = 'autopilotSessionCard';
    card.className = 'lesson-recommendation autopilot-session-card';
    card.setAttribute('aria-live', 'polite');

    const copy = document.createElement('div');
    copy.className = 'autopilot-session-copy';
    const label = document.createElement('span');
    label.textContent = 'AUTOPILOT · MY LESSON';
    title = document.createElement('strong');
    detail = document.createElement('small');
    progress = document.createElement('small');
    progress.className = 'autopilot-session-progress';
    copy.append(label, title, detail, progress);

    const controls = document.createElement('div');
    controls.className = 'autopilot-session-controls';
    startButton = document.createElement('button');
    pauseButton = document.createElement('button');
    stopButton = document.createElement('button');
    startButton.type = pauseButton.type = stopButton.type = 'button';
    startButton.textContent = 'Start My Lesson →';
    pauseButton.textContent = 'Pause';
    stopButton.textContent = 'Stop';
    pauseButton.classList.add('hidden');
    stopButton.classList.add('hidden');
    controls.append(startButton, pauseButton, stopButton);
    card.append(copy, controls);

    startButton.addEventListener('click', () => { void startSession(); });
    pauseButton.addEventListener('click', () => { void togglePause(); });
    stopButton.addEventListener('click', () => stopSession('Autopilot stopped. You can continue learning manually.'));
    return card;
  }

  function mountCard() {
    if (classroom.classList.contains('hidden') || !profileReady()) return;
    const host = document.querySelector('.learning-area');
    if (!host) return;
    const node = ensureCard();
    if (node.parentNode !== host) host.prepend(node);
    renderIdle();
  }

  function clearTimers() {
    if (session.checkTimer) clearInterval(session.checkTimer);
    if (session.nextTimer) clearTimeout(session.nextTimer);
    session.checkTimer = null;
    session.nextTimer = null;
  }

  function renderIdle() {
    if (!card || session.running) return;
    title.textContent = 'Start My Lesson';
    detail.textContent = 'Robo-Teacher will choose up to 3 learning steps from your saved progress, but you will still answer every question yourself.';
    progress.textContent = 'You can pause, stop, ask a question, or change language at any time.';
    startButton.classList.remove('hidden');
    pauseButton.classList.add('hidden');
    stopButton.classList.add('hidden');
  }

  function renderRunning(message = '') {
    ensureCard();
    startButton.classList.add('hidden');
    pauseButton.classList.remove('hidden');
    stopButton.classList.remove('hidden');
    pauseButton.textContent = session.paused ? 'Resume' : 'Pause';
    title.textContent = session.paused ? 'Autopilot paused' : 'Autopilot is guiding this lesson';
    const plan = session.currentPlan;
    detail.textContent = message || (plan ? `${plan.title}: ${plan.topic}. ${plan.reason}` : 'Choosing the best next learning step from your progress…');
    progress.textContent = `Step ${Math.min(session.completed + 1, MAX_SESSION_STEPS)} of ${MAX_SESSION_STEPS} · ${session.completed} completed`;
  }

  async function fetchPlan() {
    const token = await ensureSession();
    const response = await fetch('/api/classroom/mastery/plan', {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
      body: JSON.stringify({session_token: token, class_level: learnerClass.value})
    });
    const data = await response.json();
    if (response.status === 401) sessionToken = null;
    if (!response.ok) throw new Error(data.detail || 'I could not choose the next learning step.');
    return data;
  }

  async function openPlanPractice(plan) {
    currentProgress = currentProgress || await practiceRequest('progress', {class_level: learnerClass.value});
    currentProgress.recommended_topic = plan.topic;
    currentProgress.recommended_difficulty = plan.difficulty || currentProgress.recommended_difficulty;
    currentProgress.recommended_term = plan.term || currentProgress.recommended_term;
    openRecommendedPractice();
  }

  function openUnderstandingWhenReady(before) {
    let polls = 0;
    session.pendingCheck = false;
    if (session.checkTimer) clearInterval(session.checkTimer);
    session.checkTimer = setInterval(() => {
      polls += 1;
      if (!session.running || !session.awaitingEvidence) {
        clearInterval(session.checkTimer); session.checkTimer = null; return;
      }
      const changed = canvasAnswer.innerText.trim() && canvasAnswer.innerText.trim() !== before;
      if (changed && !understandingButton.disabled) {
        clearInterval(session.checkTimer); session.checkTimer = null;
        if (session.paused) {
          session.pendingCheck = true;
          renderRunning('The explanation is ready. Resume when you want Robo-Teacher to open the understanding check.');
        } else {
          understandingButton.click();
          renderRunning('Your turn: answer the understanding check. Autopilot will use your answer to choose what happens next.');
        }
        return;
      }
      if (polls >= CHECK_MAX_POLLS) {
        clearInterval(session.checkTimer); session.checkTimer = null;
        stopSession('The lesson response did not become ready in time. Continue manually or start a new Autopilot session.');
      }
    }, CHECK_POLL_MS);
  }

  function stopForTeacherSupport(plan) {
    const foundation = plan.foundation_for ? ` before returning to ${plan.foundation_for}` : '';
    stopSession(`Teacher support is recommended for ${plan.topic}${foundation}. Robo-Teacher has paused rather than repeating autonomous reteaching. Show your Progress view to your teacher, then continue after the topic has been reviewed together.`);
    title.textContent = 'Teacher support recommended';
    startButton.textContent = 'Review after teacher support →';
  }

  async function runPlan(plan) {
    if (plan.action === 'teacher_help') {
      stopForTeacherSupport(plan);
      return;
    }
    const before = canvasAnswer.innerText.trim();
    if (plan.action === 'practice') {
      await openPlanPractice(plan);
      renderRunning(`Complete this short ${plan.topic} practice. Robo-Teacher will choose the next step from your result.`);
      return;
    }

    window.roboTeacherPlannedMasteryCheck = plan.action === 'mastery_check';
    openChat();
    question.value = plan.prompt;
    chatForm.requestSubmit();
    renderRunning(`${plan.title}: ${plan.topic}. Listen or read, then Robo-Teacher will open one understanding check.`);
    openUnderstandingWhenReady(before);
  }

  function topicLimitReached(plan) {
    const used = session.topicActions.get(plan.topic) || 0;
    return used >= MAX_TOPIC_ACTIONS;
  }

  async function advanceSession() {
    if (!session.running || session.paused || session.awaitingEvidence) return;
    if (session.completed >= MAX_SESSION_STEPS) {
      finishSession();
      return;
    }
    try {
      renderRunning('Choosing your next best learning step…');
      const plan = await fetchPlan();
      if (!session.running || session.paused) return;
      if (plan.action !== 'teacher_help' && topicLimitReached(plan)) {
        stopSession(`${plan.topic} still needs attention. Autopilot has stopped rather than repeating the same topic again. You can ask a question, practise manually, or get help from your teacher.`);
        return;
      }
      session.currentPlan = plan;
      if (plan.action !== 'teacher_help') session.topicActions.set(plan.topic, (session.topicActions.get(plan.topic) || 0) + 1);
      session.awaitingEvidence = plan.action !== 'teacher_help';
      await runPlan(plan);
    } catch (error) {
      stopSession(error.message || 'Autopilot could not continue this lesson.');
    }
  }

  function evidenceCompletesStep(meta) {
    if (meta.source === 'practice') return true;
    if (meta.source !== 'mastery') return false;
    if (meta.stage === 'reteach') return true;
    return Boolean(meta.correct);
  }

  function onEvidence(meta) {
    if (!session.running || !session.awaitingEvidence) return;
    if (!evidenceCompletesStep(meta)) {
      renderRunning('Not quite yet. Robo-Teacher is reteaching this idea once before deciding what to do next.');
      return;
    }
    clearTimers();
    session.pendingCheck = false;
    session.awaitingEvidence = false;
    session.completed += 1;
    if (session.completed >= MAX_SESSION_STEPS) {
      finishSession();
      return;
    }
    renderRunning('Step complete. Robo-Teacher is updating your learning plan from this result…');
    if (session.paused) return;
    session.nextTimer = setTimeout(() => { void advanceSession(); }, 900);
  }

  function bindMasteryEvidence() {
    const original = window.roboTeacherMasteryRecord;
    if (typeof original !== 'function') return false;
    if (original.__autopilotSessionWrapped) return true;
    const wrapped = async function (...args) {
      const meta = args[0] || {};
      let data = await original(...args);
      const plannedConfirmation = session.running && session.currentPlan?.action === 'mastery_check' && Boolean(meta.correct) && meta.stage !== 'reteach';
      if (data?.stored && plannedConfirmation) {
        const confirmed = await original({...meta, stage: 'reteach'});
        if (confirmed?.stored) data = confirmed;
        window.roboTeacherPlannedMasteryCheck = false;
        onEvidence({source: 'mastery', correct: true, stage: 'reteach'});
        return data;
      }
      if (data?.stored) onEvidence({source: 'mastery', correct: Boolean(meta.correct), stage: meta.stage || 'initial'});
      return data;
    };
    wrapped.__autopilotSessionWrapped = true;
    window.roboTeacherMasteryRecord = wrapped;
    return true;
  }

  function waitForMasteryEvidence() {
    if (bindMasteryEvidence()) return;
    session.masteryWrapAttempts += 1;
    if (session.masteryWrapAttempts < 50) setTimeout(waitForMasteryEvidence, 200);
  }

  function bindPracticeEvidence() {
    if (session.practiceWrapped || typeof renderPracticeResults !== 'function') return;
    const original = renderPracticeResults;
    renderPracticeResults = function (...args) {
      const result = original(...args);
      if (session.running && session.awaitingEvidence && practiceMode === 'practice') {
        setTimeout(() => onEvidence({source: 'practice'}), 120);
      }
      return result;
    };
    session.practiceWrapped = true;
  }

  async function startSession() {
    if (!profileReady()) {
      setLearningStatus('Choose your learner profile before starting Autopilot', 'attention');
      return;
    }
    clearTimers();
    session.running = true;
    session.paused = false;
    session.awaitingEvidence = false;
    session.pendingCheck = false;
    session.completed = 0;
    session.currentPlan = null;
    session.topicActions = new Map();
    window.roboTeacherPlannedMasteryCheck = false;
    renderRunning('Reading your saved progress and choosing where to begin…');
    setLearningStatus('Autopilot lesson started', 'success');
    await advanceSession();
  }

  async function togglePause() {
    if (!session.running) return;
    session.paused = !session.paused;
    if (session.paused) {
      if (typeof pauseTeacherAudio === 'function' && !teacherSpeechPaused) {
        try { await pauseTeacherAudio(); } catch (_error) { /* Autopilot pause still applies. */ }
      }
      clearTimeout(session.nextTimer); session.nextTimer = null;
      renderRunning('Autopilot is paused. You can ask a question, change language, or work manually.');
      setLearningStatus('Autopilot paused', 'paused');
      return;
    }
    if (typeof resumeTeacherAudio === 'function' && teacherSpeechPaused) {
      try { await resumeTeacherAudio(); } catch (_error) { /* Continue without voice if needed. */ }
    }
    renderRunning('Autopilot resumed.');
    setLearningStatus('Autopilot resumed', 'success');
    if (session.pendingCheck && !understandingButton.disabled) {
      session.pendingCheck = false;
      understandingButton.click();
      renderRunning('Your turn: answer the understanding check.');
      return;
    }
    if (!session.awaitingEvidence) await advanceSession();
  }

  function stopSession(message) {
    clearTimers();
    session.running = false;
    session.paused = false;
    session.awaitingEvidence = false;
    session.pendingCheck = false;
    session.currentPlan = null;
    window.roboTeacherPlannedMasteryCheck = false;
    if (typeof stopTeacherAudio === 'function') {
      try { stopTeacherAudio(); } catch (_error) { /* Session can stop even if audio is already idle. */ }
    }
    ensureCard();
    title.textContent = 'Autopilot stopped';
    detail.textContent = message;
    progress.textContent = `${session.completed} of ${MAX_SESSION_STEPS} learning steps completed. Your saved progress is unchanged.`;
    startButton.textContent = session.completed ? 'Start Another Lesson →' : 'Start My Lesson →';
    startButton.classList.remove('hidden');
    pauseButton.classList.add('hidden');
    stopButton.classList.add('hidden');
    setLearningStatus(message, 'attention');
  }

  function finishSession() {
    clearTimers();
    session.running = false;
    session.paused = false;
    session.awaitingEvidence = false;
    session.pendingCheck = false;
    window.roboTeacherPlannedMasteryCheck = false;
    ensureCard();
    title.textContent = 'My lesson is complete';
    detail.textContent = `Excellent work, ${learnerNickname.value.trim()}. Robo-Teacher completed ${MAX_SESSION_STEPS} guided learning steps and saved the evidence from your answers.`;
    progress.textContent = 'Your next Autopilot session will start from your updated mastery and practice record.';
    startButton.textContent = 'Start Another Lesson →';
    startButton.classList.remove('hidden');
    pauseButton.classList.add('hidden');
    stopButton.classList.add('hidden');
    setLearningStatus('Autopilot lesson complete', 'success');
  }

  const classroomObserver = new MutationObserver(() => {
    if (!classroom.classList.contains('hidden')) setTimeout(mountCard, 100);
  });
  classroomObserver.observe(classroom, {attributes: true, attributeFilter: ['class']});

  learnerNickname.addEventListener('change', () => {
    if (session.running) stopSession('Learner changed, so Autopilot stopped safely. Start again for the new learner.');
    else setTimeout(mountCard, 50);
  });
  learnerClass.addEventListener('change', () => {
    if (session.running) stopSession('Class changed, so Autopilot stopped safely. Start again with the new curriculum level.');
    else setTimeout(mountCard, 50);
  });
  language.addEventListener('change', () => {
    if (session.running) renderRunning(`Language changed to ${language.value}. Autopilot will continue in the selected language.`);
  });

  bindPracticeEvidence();
  waitForMasteryEvidence();
  if (!classroom.classList.contains('hidden')) mountCard();
})();