(() => {
  let cachedPlan = null;
  let cachedProfile = '';
  let loadingPlan = null;
  let shownReturnProfile = '';
  let masteryWrapAttempts = 0;

  function profileKey(){return `${learnerClass.value}:${learnerNickname.value.trim().toLocaleLowerCase()}`}

  function clearPlanCache({keepReturn=false}={}){
    cachedPlan=null;cachedProfile='';loadingPlan=null;
    document.getElementById('autonomousDailyPlanCard')?.remove();
    if(!keepReturn){shownReturnProfile='';document.getElementById('autonomousReturnCard')?.remove()}
  }

  async function fetchAutonomousPlan({force=false}={}){
    const key=profileKey();
    if(!force&&cachedPlan&&cachedProfile===key)return cachedPlan;
    if(loadingPlan)return loadingPlan;
    loadingPlan=(async()=>{
      const token=await ensureSession();
      const response=await fetch('/api/classroom/mastery/plan',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({session_token:token,class_level:learnerClass.value})});
      const data=await response.json();
      if(response.status===401)sessionToken=null;
      if(!response.ok)throw new Error(data.detail||'Learning plan unavailable');
      cachedPlan=data;cachedProfile=key;return data;
    })().finally(()=>{loadingPlan=null});
    return loadingPlan;
  }

  function applyPlanToProgress(progress,plan){
    if(!progress||!plan)return progress;
    progress.autonomous_plan=plan;
    progress.recommended_topic=plan.topic;
    progress.recommended_difficulty=plan.difficulty||progress.recommended_difficulty;
    progress.recommendation=`${plan.title}: ${plan.topic}. ${plan.reason}`;
    if(plan.teacher_support_required)progress.teacher_support_required=true;
    return progress;
  }

  function ensurePlanCard(id,label){
    let card=document.getElementById(id);
    if(card)return card;
    card=document.createElement('section');card.id=id;card.className='lesson-recommendation autonomous-plan-card';card.setAttribute('aria-live','polite');
    const copy=document.createElement('div'),tag=document.createElement('span'),title=document.createElement('strong'),detail=document.createElement('small'),button=document.createElement('button');
    tag.textContent=label;button.type='button';copy.append(tag,title,detail);card.append(copy,button);return card;
  }

  function rememberedDetail(plan){
    const mastered=(plan.mastered_topics||[]).filter(Boolean);
    const support=(plan.needs_support_topics||[]).filter(Boolean);
    const remembered=mastered.length?`I remember you mastered ${mastered.slice(-2).join(' and ')}. `:'';
    if(plan.action==='teacher_help')return `${remembered}${plan.topic} has stayed difficult after repeated support. I recommend pausing Autopilot and showing this progress to your teacher.`;
    if(plan.foundation_for){
      const verb=plan.action==='reteach'?'strengthen':'quickly check';
      return `${remembered}Before we continue with ${plan.foundation_for}, I want to ${verb} ${plan.topic} because it is an important foundation.`;
    }
    if(support.length)return `${remembered}${support[0]} still needs some work, so I recommend ${plan.title.toLowerCase()} on ${plan.topic}.`;
    if(plan.action==='mastery_check')return `${remembered}You were making progress on ${plan.topic}. Let’s confirm that you can do it independently.`;
    if(plan.action==='review')return `${remembered}${plan.topic} is due for a quick spaced review so it stays strong.`;
    if(plan.action==='advance')return `${remembered}You are ready to continue with ${plan.topic}.`;
    return `${remembered}${plan.title}: ${plan.topic}. ${plan.reason}`;
  }

  function populateCard(card,plan,{welcome=false}={}){
    const title=card.querySelector('strong'),detail=card.querySelector('small'),button=card.querySelector('button');
    title.textContent=welcome?`Welcome back, ${learnerNickname.value.trim()}`:plan.title;
    detail.textContent=welcome?rememberedDetail(plan):`${plan.topic} · ${plan.term}. ${plan.reason}`;
    button.textContent=plan.button_text;button.onclick=()=>{void runPlanAction(plan)};
  }

  async function ensureProgressForPlan(plan){
    currentProgress=currentProgress||await practiceRequest('progress',{class_level:learnerClass.value});
    applyPlanToProgress(currentProgress,plan);return currentProgress;
  }

  function submitTutorPrompt(plan){
    const before=canvasAnswer.innerText.trim();
    openChat();question.value=plan.prompt;chatForm.requestSubmit();
    if(!['mastery_check','review'].includes(plan.action))return;
    let tries=0;
    const timer=setInterval(()=>{
      tries+=1;
      const changed=canvasAnswer.innerText.trim()&&canvasAnswer.innerText.trim()!==before;
      if(changed&&!understandingButton.disabled){clearInterval(timer);understandingButton.click();return}
      if(tries>=40)clearInterval(timer);
    },500);
  }

  async function runPlanAction(plan){
    try{
      if(plan.action==='teacher_help'){
        setLearningStatus(`Teacher support recommended for ${plan.topic}. Show your Progress view to your teacher before continuing this topic.`,'attention');
        if(typeof openProgress==='function')await openProgress();else progressButton?.click();
        return;
      }
      setLearningStatus(`Robo-Teacher chose: ${plan.title}`,'thinking');
      if(plan.action==='practice'){
        await ensureProgressForPlan(plan);openRecommendedPractice();return;
      }
      submitTutorPrompt(plan);
    }catch(error){setLearningStatus(error.message||'I could not start that learning step','error')}
  }

  function decorateDailyPlan(plan){
    if(!plan||dailyPlanArea.classList.contains('hidden'))return;
    const card=ensurePlanCard('autonomousDailyPlanCard','NEXT BEST ACTION');populateCard(card,plan);
    if(card.parentNode!==dailyPlanArea)dailyPlanArea.insertBefore(card,dailyPlanList);
  }

  function showReturnPlan(plan,{replace=false}={}){
    if(!plan?.has_history||classroom.classList.contains('hidden'))return;
    const key=profileKey();if(!replace&&shownReturnProfile===key)return;shownReturnProfile=key;
    const host=document.querySelector('.learning-area');if(!host)return;
    const card=ensurePlanCard('autonomousReturnCard','ROBO-TEACHER REMEMBERS');populateCard(card,plan,{welcome:true});
    if(card.parentNode!==host)host.prepend(card);
  }

  async function refreshAutonomousPlan({showReturn=false,force=false,replaceReturn=false}={}){
    try{
      const plan=await fetchAutonomousPlan({force});
      if(currentProgress)applyPlanToProgress(currentProgress,plan);
      if(showReturn)showReturnPlan(plan,{replace:replaceReturn});
      if(!dailyPlanArea.classList.contains('hidden'))decorateDailyPlan(plan);
      return plan;
    }catch(_error){return null}
  }

  async function evidenceChanged(){
    clearPlanCache({keepReturn:true});
    const plan=await refreshAutonomousPlan({showReturn:true,force:true,replaceReturn:true});
    if(plan)setLearningStatus(`Next best action updated: ${plan.title} — ${plan.topic}`,'success');
  }

  function bindMasteryRefresh(){
    const original=window.roboTeacherMasteryRecord;
    if(typeof original!=='function')return false;
    if(original.__autonomousPlannerWrapped)return true;
    const wrapped=async function(...args){
      const data=await original(...args);
      if(data?.stored)void evidenceChanged();
      return data;
    };
    wrapped.__autonomousPlannerWrapped=true;
    window.roboTeacherMasteryRecord=wrapped;
    return true;
  }

  function waitForMasteryRecorder(){
    if(bindMasteryRefresh())return;
    masteryWrapAttempts+=1;
    if(masteryWrapAttempts<40)setTimeout(waitForMasteryRecorder,250);
  }

  const baseRenderDailyPlan=renderDailyPlan;
  renderDailyPlan=function(progress){
    if(cachedPlan&&cachedProfile===profileKey())applyPlanToProgress(progress,cachedPlan);
    const result=baseRenderDailyPlan(progress);
    if(cachedPlan&&cachedProfile===profileKey())decorateDailyPlan(cachedPlan);else void refreshAutonomousPlan();
    return result;
  };

  const baseOpenDailyPlan=openDailyPlan;
  openDailyPlan=async function(){
    await refreshAutonomousPlan();
    return baseOpenDailyPlan();
  };

  if(typeof renderPracticeResults==='function'){
    const baseRenderPracticeResults=renderPracticeResults;
    renderPracticeResults=function(...args){
      const result=baseRenderPracticeResults(...args);
      setTimeout(()=>{void evidenceChanged()},80);
      return result;
    };
  }

  function resetPlan(){clearPlanCache()}
  learnerNickname.addEventListener('change',resetPlan);learnerClass.addEventListener('change',resetPlan);

  const observer=new MutationObserver(()=>{
    if(!classroom.classList.contains('hidden'))setTimeout(()=>{void refreshAutonomousPlan({showReturn:true})},120);
  });
  observer.observe(classroom,{attributes:true,attributeFilter:['class']});
  waitForMasteryRecorder();
  if(!classroom.classList.contains('hidden'))void refreshAutonomousPlan({showReturn:true});
})();