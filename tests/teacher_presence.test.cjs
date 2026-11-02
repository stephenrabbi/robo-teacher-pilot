const test=require('node:test');
const assert=require('node:assert/strict');
const {teacherPresence,renderTeacherPresence,initGestureMotion}=require('../classroom/teacher_presence.js');
test('speech and pause take precedence over lesson focus',()=>{
 assert.equal(teacherPresence({stage:'visual',speaking:true}).state,'speaking');
 assert.equal(teacherPresence({speaking:true,paused:true}).state,'paused');
 assert.equal(teacherPresence({activity:'speaking',speaking:false}).state,'ready');
});
test('listening requires an active microphone state rather than a label alone',()=>{
 assert.equal(teacherPresence({activity:'listening'}).state,'ready');
 assert.equal(teacherPresence({activity:'listening',listening:true}).state,'listening');
 assert.equal(teacherPresence({activity:'thinking'}).state,'thinking');
});
test('visual, example and check have distinct focus cues',()=>{
 for(const stage of ['visual','example','check']){const cue=teacherPresence({stage});assert.equal(cue.state,stage);assert.equal(cue.icon,'→');}
 assert.match(teacherPresence({activity:'attention'}).label,/attention/);
});
test('rendering updates only cue content and panel state',()=>{
 const doc={createElement(){return {setAttribute(k,v){this[k]=v}}}};
 const panel={dataset:{}},cue={dataset:{},ownerDocument:doc,replaceChildren(...nodes){this.children=nodes}};
 renderTeacherPresence(panel,cue,{listening:true});assert.equal(panel.dataset.teachingState,'listening');assert.equal(cue.children[0]['aria-hidden'],'true');assert.match(cue.children[1].textContent,/Listening/);
 renderTeacherPresence(panel,cue,{paused:true});assert.equal(cue.dataset.state,'paused');assert.doesNotThrow(()=>renderTeacherPresence(null,null,{}));
});
test('presenting pose yields to speech, questions, pause and preparation',()=>{
 const doc={createElement(){return {setAttribute(){}}}};
 const panel={dataset:{}},cue={dataset:{},ownerDocument:doc,replaceChildren(){}};
 for(const stage of ['visual','example','check']){
  renderTeacherPresence(panel,cue,{stage});assert.equal(panel.dataset.pose,'presenting');
  for(const state of [{speaking:true},{listening:true},{paused:true},{activity:'thinking'},{activity:'paused'}]){
   renderTeacherPresence(panel,cue,{stage,...state});assert.equal(panel.dataset.pose,'portrait');
  }
 }
 renderTeacherPresence(panel,cue,{stage:'lesson'});assert.equal(panel.dataset.pose,'portrait');
});
test('gesture motion respects manual choice and device preference changes',()=>{
 let cancelled=0;
 const panel={dataset:{},querySelectorAll(){return [{getAnimations(){return [{cancel(){cancelled++}}]}}]}},button={attrs:{},setAttribute(k,v){this.attrs[k]=v},addEventListener(_,fn){this.click=fn}};
 const preference={matches:false,addEventListener(_,fn){this.change=fn}};
 initGestureMotion(panel,button,preference);assert.equal(panel.dataset.gestureMotion,'on');
 button.click();assert.equal(panel.dataset.gestureMotion,'off');assert.equal(button.attrs['aria-pressed'],'false');assert.equal(cancelled,1);
 preference.matches=true;preference.change();assert.equal(button.disabled,true);
 preference.matches=false;preference.change();assert.equal(button.disabled,false);assert.equal(panel.dataset.gestureMotion,'off');
 button.click();assert.equal(panel.dataset.gestureMotion,'on');
 preference.matches=true;preference.change();assert.equal(panel.dataset.gestureMotion,'off');
 assert.doesNotThrow(()=>initGestureMotion(null,null,null));
});
