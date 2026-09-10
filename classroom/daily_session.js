(() => {
  const DAILY_ACTIONS=['revision','practice','lesson'];
  let dailySessionSummary=null;
  let dailySessionProgress=null;
  let dailySessionNext=null;
  let continueDailyPlan=null;
  let dailyCoachCard=null;
  let dailyCoachTitle=null;
  let dailyCoachDetail=null;
  let dailyCoachButton=null;

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

  function ensureDailyCoachCard(){
    if(dailyCoachCard)return;
    dailyCoachCard=document.createElement('section');
    dailyCoachCard.id='dailyCoachCard';
    dailyCoachCard.className='lesson-recommendation daily-coach-card hidden';
    dailyCoachCard.setAttribute('aria-live','polite');
    const copy=document.createElement('div'),label=document.createElement('span');
    dailyCoachTitle=document.createElement('strong');dailyCoachDetail=document.createElement('small');dailyCoachButton=document.createElement('button');
    label.textContent='ROBO-TEACHER GUIDANCE';dailyCoachButton.type='button';
    copy.append(label,dailyCoachTitle,dailyCoachDetail);dailyCoachCard.append(copy,dailyCoachButton);
    dailyCoachButton.addEventListener('click',()=>{
      const state=loadDailyState();hideDailyCoach();
      if(completeCount(state)===3){void openDailyPlan();return}
      continueTodayPlan();
    });
  }

  function hideDailyCoach(){if(dailyCoachCard)dailyCoachCard.classList.add('hidden')}

  function taskTitle(action){
    return dailyPlanList.querySelector(`button[data-daily-action="${action}"]`)?.closest('.daily-plan-task')?.querySelector('strong')?.textContent?.trim()||'';
  }

  function coachTarget(action){
    if(action==='revision'&&!revisionPanel.classList.contains('hidden'))return revisionPanel;
    if(action==='practice'&&!practiceResults.classList.contains('hidden'))return practiceResults;
    if(action==='lesson'&&!lessonDirector.classList.contains('hidden'))return lessonDirector;
    return document.querySelector('.learning-area');
  }

  function placeDailyCoach(action){
    ensureDailyCoachCard();
    const target=coachTarget(action);
    if(action==='practice'&&target===practiceResults){const actions=practiceResults.querySelector('.result-actions');if(actions)target.insertBefore(dailyCoachCard,actions);else target.appendChild(dailyCoachCard);return}
    if(action==='revision'&&target===revisionPanel){const actions=revisionPanel.querySelector('.revision-actions');if(actions)target.insertBefore(dailyCoachCard,actions);else target.appendChild(dailyCoachCard);return}
    if(action==='lesson'&&target===lessonDirector){target.appendChild(dailyCoachCard);return}
    const header=target?.querySelector?.('.lesson-header');if(header)header.after(dailyCoachCard);else target?.prepend?.(dailyCoachCard);
  }

  function showDailyCoach(completedAction,state,{returning=false}={}){
    ensureDailyCoachCard();
    const done=completeCount(state),next=firstIncomplete(state),nickname=learnerNickname.value.trim();
    placeDailyCoach(completedAction||next);
    if(done===3){
      const recall=dailyPlanList.dataset.revisionId?`revised ${taskTitle('revision')||'a saved lesson'}`:'kept your revision up to date';
      const strengthen=taskTitle('practice')||'your recommended topic',discover=taskTitle('lesson')||'a new topic';
      dailyCoachTitle.textContent="Today's learning complete";
      dailyCoachDetail.textContent=`Excellent work, ${nickname}. You ${recall}, practised ${strengthen}, and learned ${discover}. Your next daily plan will refresh on the next calendar day.`;
      dailyCoachButton.textContent='View completed plan ✓';
    }else if(returning){
      dailyCoachTitle.textContent=`Welcome back, ${nickname}`;
      dailyCoachDetail.textContent=`You have completed ${done} of 3 steps today. Next: ${taskTitle(next)||'continue your learning plan'}.`;
      dailyCoachButton.textContent="Continue today's plan →";
    }else if(completedAction==='revision'){
      dailyCoachTitle.textContent='Recall complete — well done';
      dailyCoachDetail.textContent=`Nice work, ${nickname}. Now strengthen ${taskTitle('practice')||'your recommended topic'} with a short personalised practice.`;
      dailyCoachButton.textContent='Continue to Strengthen →';
    }else if(completedAction==='practice'){
      dailyCoachTitle.textContent='Strengthen complete — good work';
      dailyCoachDetail.textContent=`You have finished today’s practice, ${nickname}. Next, discover ${taskTitle('lesson')||'the next topic in your learning path'} step by step with Robo-Teacher.`;
      dailyCoachButton.textContent='Continue to Discover →';
    }else{
      dailyCoachTitle.textContent='Step complete';
      dailyCoachDetail.textContent=`Good progress, ${nickname}. Next: ${taskTitle(next)||'continue your learning plan'}.`;
      dailyCoachButton.textContent="Continue today's plan →";
    }
    dailyCoachCard.classList.remove('hidden');
  }

  function restoreDailyCoach(){
    if(!dailyLearnerReady()||classroom.classList.contains('hidden')){hideDailyCoach();return}
    const state=loadDailyState(),done=completeCount(state);
    if(done>0&&done<3&&!state.activeAction){const last=[...DAILY_ACTIONS].reverse().find(action=>state.completed.includes(action))||'';showDailyCoach(last,state,{returning:true});return}
    if(done===0)hideDailyCoach();
  }

  function setDailyActiveAction(action){
    if(!DAILY_ACTIONS.includes(action)||!dailyLearnerReady())return;
    const state=loadDailyState();
    if(state.completed.includes(action))return;
    state.activeAction=action;state.activeStartedAt=Date.now();saveDailyState(state);hideDailyCoach();
  }

  function markDailyStep(action){
    if(!DAILY_ACTIONS.includes(action)||!dailyLearnerReady())return;
    const state=loadDailyState(),newlyCompleted=!state.completed.includes(action);
    if(newlyCompleted)state.completed.push(action);
    if(state.activeAction===action){state.activeAction='';state.activeStartedAt=0}
    saveDailyState(state);
    if(!dailyPlanArea.classList.contains('hidden'))renderDailyPlan(currentProgress);
    const done=completeCount(state);
    setLearningStatus(done===3?"Today's learning plan complete":`Today's plan: ${done} of 3 steps complete`,'success');
    if(newlyCompleted)showDailyCoach(action,state);
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

  const classroomObserver=new MutationObserver(()=>{if(!classroom.classList.contains('hidden')){refreshDailyPlanButton();setTimeout(restoreDailyCoach,120)}});
  classroomObserver.observe(classroom,{attributes:true,attributeFilter:['class']});
  learnerNickname.addEventListener('change',()=>{refreshDailyPlanButton();hideDailyCoach()});
  learnerClass.addEventListener('change',()=>{refreshDailyPlanButton();hideDailyCoach()});
  refreshDailyPlanButton();
})();
