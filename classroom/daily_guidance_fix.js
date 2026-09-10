(() => {
  const ACTIONS=['revision','practice','lesson'];
  const nickname=document.getElementById('learnerNickname');
  const learnerClass=document.getElementById('learnerClass');
  const todayButton=document.getElementById('dailyPlanButton');
  const dailyPlanArea=document.getElementById('dailyPlanArea');
  const dailyPlanList=document.getElementById('dailyPlanList');
  const practiceResults=document.getElementById('practiceResults');
  const revisionPanel=document.getElementById('revisionPanel');
  const lessonDirector=document.getElementById('lessonDirector');
  const canvasWork=document.getElementById('canvasWork');
  if(!nickname||!learnerClass||!todayButton||!dailyPlanList)return;

  function dateKey(){
    const d=new Date();
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
  }
  function profileReady(){return nickname.value.trim().length>=2&&/^JSS[1-3]$/.test(learnerClass.value)}
  function profileKey(){return `${learnerClass.value}:${nickname.value.trim().toLocaleLowerCase()}`}
  function storageKey(){return `roboTeacherDailySession:${profileKey()}:${dateKey()}`}
  function readState(){
    if(!profileReady())return {key:'',completed:[],activeAction:''};
    try{
      const raw=JSON.parse(localStorage.getItem(storageKey())||'null')||{};
      return {key:storageKey(),completed:Array.isArray(raw.completed)?raw.completed.filter(a=>ACTIONS.includes(a)):[],activeAction:ACTIONS.includes(raw.activeAction)?raw.activeAction:''};
    }catch(_error){return {key:storageKey(),completed:[],activeAction:''}}
  }
  function taskTitle(action){
    return dailyPlanList.querySelector(`button[data-daily-action="${action}"]`)?.closest('.daily-plan-task')?.querySelector('strong')?.textContent?.trim()||'';
  }
  function nextAction(state){return ACTIONS.find(a=>!state.completed.includes(a))||''}

  let visibleButton=null;
  function ensureCard(){
    let card=document.getElementById('dailyCoachCard');
    if(!card){
      card=document.createElement('section');card.id='dailyCoachCard';card.className='lesson-recommendation daily-coach-card hidden';card.setAttribute('aria-live','polite');
      const copy=document.createElement('div'),label=document.createElement('span'),title=document.createElement('strong'),detail=document.createElement('small'),button=document.createElement('button');
      label.textContent='ROBO-TEACHER GUIDANCE';button.type='button';copy.append(label,title,detail);card.append(copy,button);
    }
    let title=card.querySelector('strong'),detail=card.querySelector('small'),button=card.querySelector('button');
    if(button!==visibleButton){
      const clean=button.cloneNode(true);button.replaceWith(clean);button=clean;visibleButton=button;
    }
    return {card,title,detail,button};
  }
  function mount(card,action){
    let target=null,anchor=null;
    if(action==='practice'&&practiceResults&&!practiceResults.classList.contains('hidden')){target=practiceResults;anchor=target.querySelector('.result-actions')}
    else if(action==='revision'&&revisionPanel&&!revisionPanel.classList.contains('hidden')){target=revisionPanel;anchor=target.querySelector('.revision-actions')}
    else if(action==='lesson'&&canvasWork&&!canvasWork.classList.contains('hidden')){target=canvasWork.querySelector(':scope > div')||canvasWork;anchor=lessonDirector}
    else if(dailyPlanArea&&!dailyPlanArea.classList.contains('hidden')){target=dailyPlanArea;anchor=dailyPlanList}
    else target=document.querySelector('.learning-area');
    if(!target)return false;
    if(anchor&&anchor.parentNode===target)target.insertBefore(card,anchor);else target.prepend(card);
    card.classList.remove('hidden');card.style.display='flex';card.style.width='100%';card.style.marginTop='14px';
    try{card.scrollIntoView({behavior:'smooth',block:'nearest'})}catch(_error){}
    return true;
  }
  function advanceTo(action){
    if(!action)return;
    todayButton.click();
    let tries=0;
    const timer=setInterval(()=>{
      tries+=1;
      const direct=dailyPlanList.querySelector(`button[data-daily-action="${action}"]`);
      const resume=document.getElementById('continueDailyPlan');
      if(direct&&!direct.classList.contains('hidden')){clearInterval(timer);direct.click();return}
      if(resume&&!resume.disabled){clearInterval(timer);resume.click();return}
      if(tries>=20)clearInterval(timer);
    },150);
  }
  function show(action,state){
    const ui=ensureCard(),next=nextAction(state),name=nickname.value.trim();
    if(state.completed.length>=3){
      ui.title.textContent="Today's learning complete";
      ui.detail.textContent=`Excellent work, ${name}. You completed Recall, Strengthen and Discover. Your next daily plan will refresh tomorrow.`;
      ui.button.textContent='View completed plan ✓';
      ui.button.onclick=()=>todayButton.click();
    }else if(action==='revision'){
      ui.title.textContent='Recall complete — well done';
      ui.detail.textContent=`Nice work, ${name}. Next, strengthen ${taskTitle('practice')||'your recommended topic'} with a short personalised practice.`;
      ui.button.textContent='Continue to Strengthen →';ui.button.onclick=()=>advanceTo(next||'practice');
    }else if(action==='practice'){
      ui.title.textContent='Strengthen complete — good work';
      ui.detail.textContent=`You finished today’s practice, ${name}. Next, discover ${taskTitle('lesson')||'the next topic in your learning path'} step by step.`;
      ui.button.textContent='Continue to Discover →';ui.button.onclick=()=>advanceTo(next||'lesson');
    }else{
      ui.title.textContent='Step complete';ui.detail.textContent=`Good progress, ${name}. Continue with the next part of today’s learning plan.`;
      ui.button.textContent="Continue today's plan →";ui.button.onclick=()=>advanceTo(next);
    }
    mount(ui.card,action);
  }

  let previous=readState();
  function check(){
    const current=readState();
    if(current.key!==previous.key){previous=current;return}
    const newly=current.completed.find(a=>!previous.completed.includes(a));
    const genuine=newly&&previous.activeAction===newly;
    previous=current;
    if(genuine)setTimeout(()=>show(newly,readState()),60);
  }
  const observer=new MutationObserver(check);
  observer.observe(todayButton,{childList:true,subtree:true,characterData:true});
  [practiceResults,revisionPanel,lessonDirector,canvasWork,dailyPlanArea].filter(Boolean).forEach(el=>observer.observe(el,{attributes:true,attributeFilter:['class'],childList:true,subtree:true}));
  nickname.addEventListener('change',()=>{previous=readState()});
  learnerClass.addEventListener('change',()=>{previous=readState()});
})();
