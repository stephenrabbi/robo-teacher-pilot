const test=require('node:test');
const assert=require('node:assert/strict');
const {teacherPresence,renderTeacherPresence}=require('../classroom/teacher_presence.js');
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
