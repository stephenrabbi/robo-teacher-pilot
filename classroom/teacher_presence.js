/* Teaching-state cues preserve the existing portrait and audio-driven rig. */
(function(root){
 'use strict';
 function teacherPresence({activity='',stage='lesson',speaking=false,paused=false,listening=false,wakeListening=false}={}){
  if(paused)return {state:'paused',icon:'Ⅱ',label:'Paused — continue when you are ready'};
  if(speaking)return {state:'speaking',icon:'●',label:'Explaining this step'};
  if(listening)return {state:'listening',icon:'◉',label:'Listening to your question'};
  if(activity==='thinking')return {state:'thinking',icon:'◌',label:'Preparing your explanation'};
  if(activity==='attention')return {state:'attention',icon:'!',label:'Your teacher needs your attention'};
  if(activity==='paused')return {state:'paused',icon:'Ⅱ',label:'Take your time — ask your question'};
  const focus={visual:'Look at the visual',example:'Follow the worked example',check:'Try the understanding check'};
  if(focus[stage])return {state:stage,icon:'→',label:focus[stage]};
  if(wakeListening)return {state:'listening',icon:'◉',label:'Listening for Robo-Teacher'};
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
 function initGestureMotion(panel,button,preference){
  if(!panel||!button||!preference)return;
  let enabled=!preference.matches;
  const render=()=>{
   const active=enabled&&!preference.matches;
   panel.dataset.gestureMotion=active?'on':'off';button.setAttribute('aria-pressed',String(active));button.disabled=preference.matches;
   button.title=preference.matches?'Motion follows your device reduced-motion setting':'Turn the presenting arm movement on or off';
   if(!active)for(const arm of panel.querySelectorAll?.('.presenter-arm')||[])for(const animation of arm.getAnimations())animation.cancel();
  };
  button.addEventListener('click',()=>{enabled=!enabled;render();});
  preference.addEventListener('change',render);render();
 }
 if(typeof module==='object'&&module.exports)module.exports={teacherPresence,renderTeacherPresence,initGestureMotion};
 else root.RoboTeacherPresence={teacherPresence,renderTeacherPresence,initGestureMotion};
})(typeof window==='undefined'?globalThis:window);
