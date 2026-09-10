(() => {
  const DAILY_ACTIONS=['revision','practice','lesson'];
  let dailySessionSummary=null;
  let dailySessionProgress=null;
  let dailySessionNext=null;
  let continueDailyPlan=null;

  function dailyDateKey(){
    const now=new Date();
    return `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;
  }

  function dailyLearnerReady(){return learnerNickname.value.trim().length>=2&&/^JSS[1-3]$/.test(learnerClass.value)}
  function dailyStateKey(){return `roboTeacherDailySession:${lessonLibraryKey()}:${dailyDateKey()}`}
  function freshDailyState(){return {date:dailyDateKey(),completed:[],activeAction:'',activeStartedAt:0,updatedAt:Date.now()}}

  function loadDailyState(){
    if(!dailyLearnerReady())return freshDailyState();
    try{
      const parsed=JSON.parse(localStorage.getItem(dailyStateKey())||'null');
      if(!parsed||parsed.date!==dailyDateKey())return freshDailyState();
      return {
        date:parsed.date,
        completed:Array.isArray(parsed.completed)?parsed.completed.filter(action=>DAILY_ACTIONS.includes(action)):[],
        activeAction:DAILY_ACTIONS.includes(parsed.activeAction)?parsed.activeAction:'',
        activeStartedAt:Number(parsed.activeStartedAt)||0,
        updatedAt:Number(parsed.updatedAt)||Date.now()
      };
    }catch(_error){return freshDailyState()}
  }

  function saveDailyState(state){
    if(!dailyLearnerReady())return;
    state.updatedAt=Date.now();
    localStorage.setItem(dailyStateKey(),JSON.stringify(state));
    refreshDailyPlanButton(state);
  }

  function completeCount(state){return DAILY_ACTIONS.filter(action=>state.completed.includes(action)).length}
  function firstIncomplete(state){return DAILY_ACTIONS.find(action=>!state.completed.includes(action))||''}

  function refreshDailyPlanButton(state=loadDailyState()){
    if(!dailyLearnerReady()){dailyPlanButton.textContent='Today';return}
    const done=completeCount(state);
    dailyPlanButton.textContent=done===3?'Today ✓':done?`Today ${done}/3`:'Today';
    dailyPlanButton.setAttribute('aria-label',done===3?"Today's learning plan complete":done?`Continue today's learning plan. ${done} of 3 steps complete`:"Open today's learning plan");
  }

  function setDailyActiveAction(action){
    if(!DAILY_ACTIONS.includes(action)||!dailyLearnerReady())return;
    const state=loadDailyState();
    if(state.completed.includes(action))return;
    state.activeAction=action;state.activeStartedAt=Date.now();saveDailyState(state);
  }

  function markDailyStep(action){
    if(!DAILY_ACTIONS.includes(action)||!dailyLearnerReady())return;
    const state=loadDailyState();
    if(!state.completed.includes(action))state.completed.push(action);
    if(state.activeAction===action){state.activeAction='';state.activeStartedAt=0}
    saveDailyState(state);
    if(!dailyPlanArea.classList.contains('hidden'))renderDailyPlan(currentProgress);
    const done=completeCount(state);
    setLearningStatus(done===3?"Today's learning plan complete":`Today's plan: ${done} of 3 steps complete`,'success');
  }

  function ensureDailySessionSummary(){
    if(dailySessionSummary)return;
    dailySessionSummary=document.createElement('section');
    dailySessionSummary.id='dailySessionSummary';
    dailySessionSummary.className='lesson-recommendation daily-session-summary';
    dailySessionSummary.setAttribute('aria-live','polite');
    const copy=document.createElement('div'),label=document.createElement('span');
    dailySessionProgress=document.createElement('strong');dailySessionNext=document.createElement('small');
    continueDailyPlan=document.createElement('button');
    label.textContent='YOUR PROGRESS';dailySessionProgress.textContent='0 of 3 steps complete';dailySessionNext.textContent='Start with your first step.';
    continueDailyPlan.id='continueDailyPlan';continueDailyPlan.type='button';continueDailyPlan.textContent="Continue today's plan →";
    copy.append(label,dailySessionProgress,dailySessionNext);dailySessionSummary.append(copy,continueDailyPlan);
    const intro=dailyPlanArea.querySelector('.daily-plan-intro');
    if(intro)intro.after(dailySessionSummary);else dailyPlanArea.prepend(dailySessionSummary);
    continueDailyPlan.addEventListener('click',continueTodayPlan);
  }

  function taskLabel(action){
    const card=dailyPlanList.querySelector(`button[data-daily-action="${action}"]`)?.closest('.daily-plan-task');
    const kind=card?.querySelector('small')?.textContent?.trim();
    const title=card?.querySelector('strong')?.textContent?.trim();
    return [kind,title].filter(Boolean).join(' · ');
  }

  function updateDailySessionSummary(state){
    ensureDailySessionSummary();
    const done=completeCount(state),active=state.activeAction&&!state.completed.includes(state.activeAction)?state.activeAction:firstIncomplete(state);
    dailySessionProgress.textContent=done===3?'All 3 steps complete':`${done} of 3 steps complete`;
    dailySessionNext.textContent=done===3?'Excellent work. Your plan will refresh on the next calendar day.':`Next: ${taskLabel(active)||'continue your learning session'}`;
    continueDailyPlan.disabled=done===3;
    continueDailyPlan.textContent=done===3?'Today complete ✓':"Continue today's plan →";
  }

  function matchingDailyLessonSnapshot(state){
    if(state.activeAction!=='lesson')return null;
    const snapshot=loadClassroomSnapshot();
    if(!snapshot||snapshot.classLevel!==learnerClass.value||snapshot.nickname.trim().toLocaleLowerCase()!==learnerNickname.value.trim().toLocaleLowerCase())return null;
    if(state.activeStartedAt&&Number(snapshot.savedAt)<state.activeStartedAt)return null;
    return snapshot;
  }

  function resumeDailyLesson(snapshot){
    dailyPlanArea.classList.add('hidden');dismissLessonOverlays();whiteboardArea.classList.add('hidden');practiceArea.classList.add('hidden');progressArea.classList.add('hidden');
    canvasEmpty.classList.add('hidden');canvasWork.classList.remove('hidden');canvasStatus.textContent=snapshot.canvasStatus||"Today's lesson restored";
    const autoTeachWasEnabled=lessonChoreography.enabled;lessonChoreography.enabled=false;startLessonDirector(snapshot.answer,snapshot.lessonIndex||0);lessonChoreography.enabled=autoTeachWasEnabled;
    readAnswerButton.disabled=false;setActiveMode(chatButton);setLearningStatus("Continuing today's lesson",'success');keepTeachingCanvasVisible();
  }

  function continueTodayPlan(){
    const state=loadDailyState();
    if(completeCount(state)===3){setLearningStatus("Today's learning plan is complete",'success');return}
    const action=state.activeAction&&!state.completed.includes(state.activeAction)?state.activeAction:firstIncomplete(state);
    if(action==='lesson'){
      const snapshot=matchingDailyLessonSnapshot(state);
      if(snapshot){resumeDailyLesson(snapshot);return}
    }
    const button=dailyPlanList.querySelector(`button[data-daily-action="${action}"]`);
    if(button&&!button.classList.contains('hidden'))button.click();
  }

  const baseRenderDailyPlan=renderDailyPlan;
  renderDailyPlan=function(progress){
    baseRenderDailyPlan(progress);
    const state=loadDailyState();
    const dueLessonId=dailyPlanList.dataset.revisionId;
    if(!dueLessonId&&!state.completed.includes('revision'))state.completed.push('revision');
    DAILY_ACTIONS.forEach(action=>{
      if(!state.completed.includes(action))return;
      const button=dailyPlanList.querySelector(`button[data-daily-action="${action}"]`),card=button?.closest('.daily-plan-task');
      if(!card)return;
      card.dataset.complete='true';const marker=card.querySelector(':scope > span');if(marker)marker.textContent='✓';button.classList.add('hidden');
    });
    if(!dueLessonId&&state.activeAction==='revision'){state.activeAction='';state.activeStartedAt=0}
    saveDailyState(state);updateDailySessionSummary(state);
    const done=completeCount(state);
    setLearningStatus(done===3?"Today's plan is complete":done?`Continue today's plan — ${done} of 3 complete`:"Today's plan is ready",'success');
  };

  dailyPlanList.addEventListener('click',event=>{
    const button=event.target.closest('button[data-daily-action]');
    if(button)setDailyActiveAction(button.dataset.dailyAction);
  });

  const baseRecordRevisionResult=recordRevisionResult;
  recordRevisionResult=function(){
    const result=baseRecordRevisionResult();
    const state=loadDailyState();if(state.activeAction==='revision')markDailyStep('revision');
    return result;
  };

  const baseRenderPracticeResults=renderPracticeResults;
  renderPracticeResults=function(summary){
    const result=baseRenderPracticeResults(summary);
    const state=loadDailyState();if(practiceMode==='practice'&&state.activeAction==='practice')markDailyStep('practice');
    return result;
  };

  const baseRenderCurrentLessonStep=renderCurrentLessonStep;
  renderCurrentLessonStep=function(){
    const result=baseRenderCurrentLessonStep();
    const state=loadDailyState();
    if(state.activeAction==='lesson'&&currentLesson&&currentLesson.index===currentLesson.steps.length-1)markDailyStep('lesson');
    return result;
  };

  const classroomObserver=new MutationObserver(()=>{if(!classroom.classList.contains('hidden'))refreshDailyPlanButton()});
  classroomObserver.observe(classroom,{attributes:true,attributeFilter:['class']});
  learnerNickname.addEventListener('change',()=>refreshDailyPlanButton());
  learnerClass.addEventListener('change',()=>refreshDailyPlanButton());
  refreshDailyPlanButton();
})();
