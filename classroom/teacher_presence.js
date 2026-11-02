/* Teaching-state cues preserve the existing portrait and audio-driven rig. */
(function(root){
 'use strict';
 function teacherPresence({activity='',stage='lesson',speaking=false,paused=false,listening=false}={}){
  if(paused)return {state:'paused',icon:'Ⅱ',label:'Paused — continue when you are ready'};
  if(speaking)return {state:'speaking',icon:'●',label:'Explaining this step'};
  if(listening)return {state:'listening',icon:'◉',label:'Listening to your question'};
  if(activity==='thinking')return {state:'thinking',icon:'◌',label:'Preparing your explanation'};
  if(activity==='attention')return {state:'attention',icon:'!',label:'Your teacher needs your attention'};
  if(activity==='paused')return {state:'paused',icon:'Ⅱ',label:'Take your time — ask your question'};
  const focus={visual:'Look at the visual',example:'Follow the worked example',check:'Try the understanding check'};
  if(focus[stage])return {state:stage,icon:'→',label:focus[stage]};
  return {state:'ready',icon:'●',label:'Ready to guide you step by step'};
 }
 function renderTeacherPresence(panel,cue,options){
  if(!panel||!cue)return;
  const value=teacherPresence(options);panel.dataset.teachingState=value.state;cue.dataset.state=value.state;
  panel.dataset.pose=['visual','example','check'].includes(value.state)?'presenting':'portrait';
  const icon=cue.ownerDocument.createElement('span');icon.className='teacher-cue-icon';icon.setAttribute('aria-hidden','true');icon.textContent=value.icon;
  const text=cue.ownerDocument.createElement('span');text.textContent=value.label;
  cue.replaceChildren(icon,text);
 }
 if(typeof module==='object'&&module.exports)module.exports={teacherPresence,renderTeacherPresence};
 else root.RoboTeacherPresence={teacherPresence,renderTeacherPresence};
})(typeof window==='undefined'?globalThis:window);
