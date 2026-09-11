(() => {
  const setup=document.getElementById('practiceSetup');
  const selectors=setup?.querySelector('.practice-selectors');
  const learnerClass=document.getElementById('learnerClass');
  const practiceButton=document.getElementById('practiceButton');
  const startLearning=document.getElementById('startLearning');
  const practiceClass=document.getElementById('practiceClass');
  const practiceTerm=document.getElementById('practiceTerm');
  const practiceTopic=document.getElementById('practiceTopic');
  const practiceDifficulty=document.getElementById('practiceDifficulty');
  const practiceCount=document.getElementById('practiceCount');
  const title=document.getElementById('practiceTitle');
  if(!setup||!selectors||!learnerClass||!practiceClass||!practiceTerm||!practiceTopic||!practiceDifficulty||!practiceCount)return;
  if(setup.dataset.practiceUxReady==='true')return;

  const classLabel=practiceClass.closest('label');
  const termLabel=practiceTerm.closest('label');
  const topicLabel=practiceTopic.closest('label');
  const difficultyLabel=practiceDifficulty.closest('label');
  const countLabel=practiceCount.closest('label');
  if(!classLabel||!termLabel||!topicLabel||!difficultyLabel||!countLabel)return;

  if(title)title.textContent='Choose a topic to practise';
  selectors.classList.add('practice-simplified');
  classLabel.classList.add('practice-class-auto');
  topicLabel.classList.add('practice-topic-primary');

  const quickSummary=document.createElement('p');
  quickSummary.className='practice-quick-summary';
  quickSummary.setAttribute('aria-live','polite');

  const customize=document.createElement('details');
  customize.className='practice-customize';
  const customizeSummary=document.createElement('summary');
  customizeSummary.textContent='Customize practice';
  customizeSummary.setAttribute('aria-label','Customize term, difficulty and number of questions');
  const advanced=document.createElement('div');
  advanced.className='practice-customize-grid';
  advanced.append(termLabel,difficultyLabel,countLabel);
  customize.append(customizeSummary,advanced);

  selectors.append(topicLabel,quickSummary,customize,classLabel);

  function optionText(select){return select.options[select.selectedIndex]?.textContent?.trim()||select.value;}
  function refreshSummary(){
    quickSummary.textContent=`${practiceClass.value} · ${optionText(practiceDifficulty)} · ${optionText(practiceCount)}`;
  }
  function syncClass(){
    const target=learnerClass.value;
    if(/^JSS[1-3]$/.test(target)&&practiceClass.value!==target){
      practiceClass.value=target;
      practiceClass.dispatchEvent(new Event('change',{bubbles:true}));
    }
    refreshSummary();
  }

  [practiceTerm,practiceDifficulty,practiceCount,practiceClass].forEach(select=>select.addEventListener('change',refreshSummary));
  learnerClass.addEventListener('change',syncClass);
  startLearning?.addEventListener('click',()=>setTimeout(syncClass,0));
  practiceButton?.addEventListener('click',()=>setTimeout(syncClass,0));

  const style=document.createElement('style');
  style.id='robo-teacher-practice-layout';
  style.textContent=`
    .practice-selectors.practice-simplified{
      display:grid;
      grid-template-columns:1fr;
      gap:10px;
      margin-bottom:14px;
    }
    .practice-selectors.practice-simplified>.practice-class-auto{display:none!important}
    .practice-topic-primary{
      padding:14px;
      border:1px solid #c8d8ea;
      border-radius:14px;
      background:#f7fbff;
    }
    .practice-topic-primary select{margin-top:2px}
    .practice-quick-summary{
      margin:0;
      color:#41536a;
      font-size:13px;
      font-weight:700;
    }
    .practice-customize{
      border:1px solid #c8d8ea;
      border-radius:12px;
      background:#fff;
      overflow:hidden;
    }
    .practice-customize>summary{
      min-height:44px;
      display:flex;
      align-items:center;
      justify-content:space-between;
      padding:10px 13px;
      color:#17355e;
      font-size:14px;
      font-weight:800;
      cursor:pointer;
      list-style:none;
      user-select:none;
    }
    .practice-customize>summary::-webkit-details-marker{display:none}
    .practice-customize>summary::after{content:'+';font-size:20px;line-height:1}
    .practice-customize[open]>summary::after{content:'−'}
    .practice-customize-grid{
      display:grid;
      grid-template-columns:repeat(3,minmax(0,1fr));
      gap:10px;
      padding:0 12px 12px;
      border-top:1px solid #e0e8f2;
      padding-top:12px;
    }
    .practice-customize-grid label{min-width:0}
    @media(max-width:600px){
      .practice-topic-primary{padding:11px}
      .practice-customize-grid{grid-template-columns:1fr}
    }
  `;
  document.head.appendChild(style);
  syncClass();
  setup.dataset.practiceUxReady='true';
})();
