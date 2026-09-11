(() => {
  if(document.getElementById('roboTeacherWelcomeLayoutStyles'))return;

  const style=document.createElement('style');
  style.id='roboTeacherWelcomeLayoutStyles';
  style.textContent=`
    .welcome-screen{
      grid-template-columns:minmax(240px,.66fr) minmax(480px,1.34fr);
      gap:34px;
    }
    .welcome-screen .founder-panel{
      width:min(100%,420px);
      margin-inline:auto;
    }
    .welcome-copy{
      max-width:820px;
    }
    .welcome-copy h1{
      margin-bottom:18px;
    }
    .speech-card{
      padding:24px 26px;
      border-radius:22px;
    }
    .speech-card p{
      margin:8px 0;
    }
    .learner-onboarding{
      margin-top:14px;
      padding-top:14px;
    }
    .welcome-actions{
      display:flex;
      flex-wrap:wrap;
      gap:9px;
      align-items:center;
      margin-top:16px;
    }
    .welcome-actions .primary{
      flex:1 1 100%;
      order:0;
      margin:0;
      min-height:56px;
      font-size:17px;
    }
    #resumeLearning{
      order:1;
      min-height:44px;
    }
    #hearFounder,#showTeacherLogin{
      min-height:44px;
      margin:0;
      padding:10px 14px;
      border-radius:11px;
      font-size:14px;
      font-weight:700;
      cursor:pointer;
    }
    #hearFounder{
      order:2;
      border:1px solid #8aa0bd;
      background:#f7f9fc;
      color:#17355e;
    }
    #showTeacherLogin{
      order:3;
      border:1px solid transparent;
      background:transparent;
      color:#34445c;
      text-decoration:underline;
      text-underline-offset:3px;
    }
    .privacy-note{
      margin-top:12px;
      color:#46566d;
    }
    @media(max-width:900px){
      .welcome-screen{
        grid-template-columns:1fr;
        gap:16px;
      }
      .welcome-screen .founder-panel{
        width:min(100%,300px);
      }
      .welcome-copy{
        max-width:none;
      }
    }
    @media(max-width:600px){
      .welcome-screen .founder-panel{
        width:min(100%,250px);
      }
      .speech-card{
        padding:17px;
      }
      .welcome-actions{
        gap:7px;
      }
      #hearFounder,#showTeacherLogin,#resumeLearning{
        flex:1 1 auto;
      }
    }
  `;
  document.head.appendChild(style);

  const start=document.getElementById('startLearning');
  const hear=document.getElementById('hearFounder');
  const teacher=document.getElementById('showTeacherLogin');
  if(start)start.setAttribute('aria-describedby','onboardingPrimaryHint');

  const onboarding=document.querySelector('.learner-onboarding');
  if(onboarding&&!document.getElementById('onboardingPrimaryHint')){
    const hint=document.createElement('p');
    hint.id='onboardingPrimaryHint';
    hint.textContent='Choose your nickname and class, then start learning.';
    hint.style.gridColumn='1 / -1';
    hint.style.margin='2px 0 0';
    hint.style.fontSize='13px';
    hint.style.color='#46566d';
    onboarding.appendChild(hint);
  }

  if(hear)hear.title='Optional: hear Herbert welcome you';
  if(teacher)teacher.title='For teachers with a private access key';
})();
