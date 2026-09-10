(() => {
  const ACTIONS=['revision','practice','lesson'];
  const nickname=document.getElementById('learnerNickname');
  const learnerClass=document.getElementById('learnerClass');
  const classroom=document.getElementById('classroom');
  const startButton=document.getElementById('startLearning');
  const resumeButton=document.getElementById('resumeLearning');
  const todayButton=document.getElementById('dailyPlanButton');
  const dailyPlanList=document.getElementById('dailyPlanList');
  if(!nickname||!learnerClass||!classroom||!todayButton||!dailyPlanList)return;

  function dateKey(){
    const d=new Date();
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
  }
  function ready(){return nickname.value.trim().length>=2&&/^JSS[1-3]$/.test(learnerClass.value)}
  function stateKey(){return `roboTeacherDailySession:${learnerClass.value}:${nickname.value.trim().toLocaleLowerCase()}:${dateKey()}`}
  function readState(){
    if(!ready())return {completed:[],activeAction:''};
    try{
      const raw=JSON.parse(localStorage.getItem(stateKey())||'null')||{};
      return {
        completed:Array.isArray(raw.completed)?raw.completed.filter(action=>ACTIONS.includes(action)):[],
        activeAction:ACTIONS.includes(raw.activeAction)?raw.activeAction:''
      };
    }catch(_error){return {completed:[],activeAction:''}}
  }
  function nextAction(state){return ACTIONS.find(action=>!state.completed.includes(action))||''}
  function taskTitle(action){
    return dailyPlanList.querySelector(`button[data-daily-action="${action}"]`)?.closest('.daily-plan-task')?.querySelector('strong')?.textContent?.trim()||'';
  }

  let shownFor='';
  function advance(action){
    if(!action)return;
    todayButton.click();
    let attempts=0;
    const timer=setInterval(()=>{
      attempts+=1;
      const direct=dailyPlanList.querySelector(`button[data-daily-action="${action}"]`);
      const resume=document.getElementById('continueDailyPlan');
      if(direct&&!direct.classList.contains('hidden')){clearInterval(timer);direct.click();return}
      if(resume&&!resume.disabled){clearInterval(timer);resume.click();return}
      if(attempts>=24)clearInterval(timer);
    },150);
  }

  function showReturning(){
    if(classroom.classList.contains('hidden')||!ready())return false;
    const state=readState(),done=state.completed.length;
    if(done<=0||done>=3||state.activeAction)return false;
    const key=stateKey();
    if(shownFor===key)return true;

    let card=document.getElementById('dailyCoachCard');
    if(!card){
      card=document.createElement('section');
      card.id='dailyCoachCard';
      card.className='lesson-recommendation daily-coach-card';
      card.setAttribute('aria-live','polite');
      const copy=document.createElement('div');
      const label=document.createElement('span');
      const title=document.createElement('strong');
      const detail=document.createElement('small');
      const button=document.createElement('button');
      label.textContent='ROBO-TEACHER GUIDANCE';
      button.type='button';
      copy.append(label,title,detail);
      card.append(copy,button);
    }

    const next=nextAction(state);
    const title=card.querySelector('strong');
    const detail=card.querySelector('small');
    let button=card.querySelector('button');
    const cleanButton=button.cloneNode(true);
    button.replaceWith(cleanButton);
    button=cleanButton;

    title.textContent=`Welcome back, ${nickname.value.trim()}`;
    detail.textContent=`You have completed ${done} of 3 steps today. Next: ${taskTitle(next)||'continue your learning plan'}.`;
    button.textContent="Continue today's plan →";
    button.addEventListener('click',()=>advance(next));

    const area=document.querySelector('.learning-area');
    const header=area?.querySelector('.lesson-header');
    if(!area)return false;
    if(header)header.after(card);else area.prepend(card);
    card.classList.remove('hidden');
    card.style.display='flex';
    card.style.width='100%';
    card.style.marginBottom='14px';
    shownFor=key;
    try{card.scrollIntoView({behavior:'smooth',block:'nearest'})}catch(_error){}
    return true;
  }

  function schedule(){
    [120,400,900,1600].forEach(delay=>setTimeout(showReturning,delay));
  }

  const classroomObserver=new MutationObserver(()=>{
    if(!classroom.classList.contains('hidden'))schedule();
  });
  classroomObserver.observe(classroom,{attributes:true,attributeFilter:['class']});

  startButton?.addEventListener('click',schedule);
  resumeButton?.addEventListener('click',schedule);
  window.addEventListener('pageshow',schedule);
  document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')schedule()});
  nickname.addEventListener('input',()=>{shownFor=''});
  learnerClass.addEventListener('change',()=>{shownFor=''});
})();
