const test=require('node:test');
const assert=require('node:assert/strict');
const {teacherPresence,renderTeacherPresence,initGestureMotion,mathsGestureTopic}=require('../classroom/teacher_presence.js');
test('speech and pause take precedence over lesson focus',()=>{
 assert.equal(teacherPresence({stage:'visual',speaking:true}).state,'speaking');
 assert.equal(teacherPresence({speaking:true,paused:true}).state,'paused');
 assert.equal(teacherPresence({activity:'speaking',speaking:false}).state,'ready');
});
test('active narration keeps speaking avatar even while wake microphone listens',()=>{
 const state=teacherPresence({speaking:true,listening:true,wakeListening:true,paused:false});
 assert.equal(state.state,'speaking');
 assert.match(state.label,/Explaining this step/);
 const doc={createElement(){return {setAttribute(){}}}};
 const panel={dataset:{}},cue={dataset:{},ownerDocument:doc,replaceChildren(...nodes){this.children=nodes}};
 renderTeacherPresence(panel,cue,{speaking:true,listening:true,paused:false});
 assert.equal(panel.dataset.teachingState,'speaking');
 assert.equal(panel.dataset.pose,'portrait');
 assert.match(cue.children[1].textContent,/Explaining/);
 // During barge-in, narration pauses and the microphone remains active.
 renderTeacherPresence(panel,cue,{speaking:false,listening:true,paused:true});
 assert.equal(panel.dataset.teachingState,'listening');
 // Once microphone listening ends, remain visibly paused, not listening.
 renderTeacherPresence(panel,cue,{speaking:false,listening:false,paused:true});
 assert.equal(panel.dataset.teachingState,'paused');
 // On resume, display the talking face again even if wake listening persists.
 renderTeacherPresence(panel,cue,{speaking:true,listening:true,paused:false});
 assert.equal(panel.dataset.teachingState,'speaking');
});

test('voice interruption shows listening instead of paused while microphone is active',()=>{
 const state=teacherPresence({paused:true,listening:true,stage:'lesson'});
 assert.equal(state.state,'listening');
 assert.match(state.label,/Listening to your question/);
 assert.equal(teacherPresence({paused:true,listening:false}).state,'paused');
 const doc={createElement(){return {setAttribute(){}}}};
 const panel={dataset:{}},cue={dataset:{},ownerDocument:doc,replaceChildren(...nodes){this.children=nodes}};
 renderTeacherPresence(panel,cue,{paused:true,listening:true});
 assert.equal(panel.dataset.teachingState,'listening');
 assert.equal(panel.dataset.pose,'portrait');
 assert.match(cue.children[1].textContent,/Listening/);
 renderTeacherPresence(panel,cue,{speaking:true,listening:false,paused:false});
 assert.equal(panel.dataset.teachingState,'speaking');
});

test('listening requires an active microphone state rather than a label alone',()=>{
 assert.equal(teacherPresence({activity:'listening'}).state,'ready');
 assert.equal(teacherPresence({activity:'listening',listening:true}).state,'listening');
 assert.equal(teacherPresence({activity:'thinking'}).state,'thinking');
});
test('visual, example and check have distinct focus cues',()=>{
 for(const stage of ['visual','example','check']){const cue=teacherPresence({stage});assert.equal(cue.state,stage);assert.equal(cue.icon,'→');}
 assert.match(teacherPresence({activity:'attention'}).label,/attention/);
 assert.equal(teacherPresence({wakeListening:true}).state,'listening');
 assert.equal(teacherPresence({stage:'visual',wakeListening:true}).state,'visual');
 assert.equal(teacherPresence({stage:'visual',wakeListening:true,listening:true}).state,'listening');
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

test('Maths gesture selection follows lesson content and avoids generic words',()=>{
 assert.equal(mathsGestureTopic('Solve 3x + 5 = 20 by subtraction'),'calculation');
 assert.equal(mathsGestureTopic('Plot the coordinate (2, 3) on the graph'),'graph');
 assert.equal(mathsGestureTopic('Find the gradient of the line'),'graph');
 assert.equal(mathsGestureTopic('Draw a triangle and measure its angle'),'geometry');
 assert.equal(mathsGestureTopic('Find the circumference of a circle'),'geometry');
 assert.equal(mathsGestureTopic('Find the area under the graph'),'graph');
 assert.equal(mathsGestureTopic('Compare 7 and 12'),'calculation');
 assert.equal(mathsGestureTopic(null),'calculation');
});
