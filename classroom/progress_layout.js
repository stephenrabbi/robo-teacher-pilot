(() => {
  const dashboard=document.getElementById('progressDashboard');
  const recommendation=dashboard?.querySelector('.progress-recommendation');
  const stats=dashboard?.querySelector('.progress-stats');
  const progressArea=document.getElementById('progressArea');
  if(!dashboard||!recommendation||!stats||!progressArea)return;

  recommendation.classList.add('progress-action-first');
  dashboard.insertBefore(recommendation,stats);

  const style=document.createElement('style');
  style.id='roboTeacherProgressActionStyles';
  style.textContent=`
    #progressDashboard{display:flex;flex-direction:column;gap:14px}
    #progressDashboard.hidden{display:none!important}
    .progress-action-first{order:-10;margin:0;background:linear-gradient(135deg,#eaf3ff 0,#f8fbff 100%);border:1px solid #9fc4f3;border-left:5px solid #1677ff;box-shadow:0 10px 28px rgba(16,44,83,.08);padding:16px 17px}
    .progress-action-first span{color:#0757c9!important;font-size:11px!important;letter-spacing:.8px!important}
    .progress-action-first strong{font-size:18px;line-height:1.45;color:#10203a}
    .progress-action-first button{background:#1677ff!important;border-color:#1677ff!important;min-height:44px}
    .progress-stats{order:-5}
    @media(max-width:700px){
      .progress-action-first{grid-template-columns:1fr!important;gap:8px!important;padding:14px}
      .progress-action-first button{grid-column:1!important;grid-row:auto!important;width:100%;margin-top:4px!important}
      .progress-action-first strong{font-size:17px}
    }
  `;
  document.head.appendChild(style);

  const heading=progressArea.querySelector('.progress-heading');
  if(heading){
    let helper=document.getElementById('progressActionHelper');
    if(!helper){
      helper=document.createElement('p');
      helper.id='progressActionHelper';
      helper.textContent='Start with the recommended next step, then review your learning data below.';
      helper.style.cssText='margin:-8px 0 14px;color:#46566d;font-size:14px;line-height:1.5';
      heading.after(helper);
    }
  }
})();
