(() => {
  let cachedPlan = null;
  let cachedProfile = '';
  let loadingPlan = null;
  let shownReturnProfile = '';

  function profileKey(){return `${learnerClass.value}:${learnerNickname.value.trim().toLocaleLowerCase()}`}

  async function fetchAutonomousPlan(){
    const key=profileKey();
    if(cachedPlan&&cachedProfile===key)return cachedPlan;
    if(loadingPlan)return loadingPlan;
    loadingPlan=(async()=>{
      const token=await ensureSession();
      const response=await fetch('/api/classroom/mastery/plan',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({session_token:token,class_level:learnerClass.value})});
      const data=await response.json();
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
    return progress;
  }

  function ensurePlanCard(id,label){
    let card=document.getElementById(id);
    if(card)return card;
    card=document.createElement('section');card.id=id;card.className='lesson-recommendation autonomous-plan-card';card.setAttribute('aria-live','polite');
    const copy=document.createElement('div'),tag=document.createElement('span'),title=document.createElement('strong'),detail=document.createElement('small'),button=document.createElement('button');
    tag.textContent=label;button.type='button';copy.append(tag,title,detail);card.append(copy,button);return card;
  }

  function populateCard(card,plan,{welcome=false}={}){
    const title=card.querySelector('strong'),detail=card.querySelector('small'),button=card.querySelector('button');
    title.textContent=welcome?`Welcome back, ${learnerNickname.value.trim()}`:plan.title;
    detail.textContent=welcome?`${plan.title}: ${plan.topic}. ${plan.reason}`:`${plan.topic} · ${plan.term}. ${plan.reason}`;
    button.textContent=plan.button_text;button.onclick=()=>{void runPlanAction(plan)};
  }

  async function ensureProgressForPlan(plan){
    currentProgress=currentProgress||await practiceRequest('progress',{class_level:learnerClass.value});
    applyPlanToProgress(currentProgress,plan);return currentProgress;
  }

  function submitTutorPrompt(plan){
    const before=canvasAnswer.innerText.trim();
    openChat();question.value=plan.prompt;chatForm.requestSubmit();
    if(plan.action!=='mastery_check')return;
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

  function showReturnPlan(plan){
    if(!plan?.has_history||classroom.classList.contains('hidden'))return;
    const key=profileKey();if(shownReturnProfile===key)return;shownReturnProfile=key;
    const host=document.querySelector('.learning-area');if(!host)return;
    const card=ensurePlanCard('autonomousReturnCard','ROBO-TEACHER REMEMBERS');populateCard(card,plan,{welcome:true});
    host.prepend(card);
  }

  async function refreshAutonomousPlan({showReturn=false}={}){
    try{
      const plan=await fetchAutonomousPlan();
      if(currentProgress)applyPlanToProgress(currentProgress,plan);
      if(showReturn)showReturnPlan(plan);
      if(!dailyPlanArea.classList.contains('hidden'))decorateDailyPlan(plan);
      return plan;
    }catch(_error){return null}
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

  function resetPlan(){cachedPlan=null;cachedProfile='';shownReturnProfile='';document.getElementById('autonomousReturnCard')?.remove();document.getElementById('autonomousDailyPlanCard')?.remove()}
  learnerNickname.addEventListener('change',resetPlan);learnerClass.addEventListener('change',resetPlan);

  const observer=new MutationObserver(()=>{
    if(!classroom.classList.contains('hidden'))setTimeout(()=>{void refreshAutonomousPlan({showReturn:true})},120);
  });
  observer.observe(classroom,{attributes:true,attributeFilter:['class']});
  if(!classroom.classList.contains('hidden'))void refreshAutonomousPlan({showReturn:true});
})();
