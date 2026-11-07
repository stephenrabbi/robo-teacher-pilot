const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync('classroom/app.js','utf8');
function harness(){
 const ctx={currentLesson:{text:'Original lesson',index:1,steps:['Intro','Translated graph step','Check']},lessonHistory:[],lessonInterruption:null,lessonDirector:{classList:{toggle(){}}},startLessonDirector(text,index,steps){ctx.currentLesson={text,index,steps}}};
 vm.createContext(ctx);
 vm.runInContext(source.slice(source.indexOf('function captureLessonCheckpoint(){'),source.indexOf('function loadClassroomSnapshot(){')),ctx);
 return ctx;
}
test('nested questions return through exact steps without aliasing',()=>{
 const c=harness();const original=c.captureLessonCheckpoint();c.lessonHistory.push(original);
 c.currentLesson.steps[1]='changed';
 c.currentLesson={text:'Answer',index:0,steps:['Answer to interruption']};
 c.lessonHistory.push(c.captureLessonCheckpoint());
 c.currentLesson={text:'Follow up',index:0,steps:['Follow-up answer']};
 c.restoreLessonCheckpoint(c.lessonHistory.pop());assert.equal(c.currentLesson.steps[0],'Answer to interruption');
 c.restoreLessonCheckpoint(c.lessonHistory.pop());assert.equal(c.currentLesson.index,1);assert.equal(c.currentLesson.steps[1],'Translated graph step');
});
test('a serialized reload retains the original return destination',()=>{
 const c=harness();const original=c.captureLessonCheckpoint();
 const snapshot=JSON.parse(JSON.stringify({lessonHistory:[original],lessonInterruption:original}));
 c.restoreLessonHistory(snapshot);c.restoreLessonCheckpoint(c.lessonHistory.pop());
 assert.equal(c.currentLesson.index,1);assert.equal(c.lessonInterruption.step,'Translated graph step');
});
test('restoration clears another learner history and rejects malformed entries',()=>{
 const c=harness();c.lessonHistory.push(c.captureLessonCheckpoint());
 c.restoreLessonHistory({lessonHistory:[{text:'Bad',index:8,steps:['Only one']}],lessonInterruption:{text:'Bad',index:-1,steps:['x']}});
 assert.equal(c.lessonHistory.length,0);assert.equal(c.lessonInterruption,null);
 c.restoreLessonHistory({});assert.equal(c.lessonHistory.length,0);
});

test('serialized question history retains the exact example return point',()=>{
 const c=harness();const checkpoint=c.captureLessonCheckpoint();checkpoint.example={title:'Worked example',source:'Synthetic',steps:['First','Exact second step'],index:1};checkpoint.step='Exact second step';
 c.restoreLessonHistory(JSON.parse(JSON.stringify({lessonHistory:[checkpoint]})));
 let restored;c.restoreWorkedExample=example=>{restored=example};c.restoreLessonCheckpoint(c.lessonHistory.pop());
 assert.equal(restored.index,1);assert.equal(restored.steps[1],'Exact second step');assert.equal(c.currentLesson.steps[1],'Translated graph step');
});

test('example restoration accepts bounded replay data and rejects invalid or external payloads',()=>{
 let renders=0;const classes={add(){},remove(){}};
 const c={lessonChoreography:{timer:null},clearTimeout(){},dismissLessonOverlays(){},renderLessonMedia(data,index){renders++;assert.equal(data.kind,'replay');assert.equal(index,1)},canvasWork:{classList:classes},canvasEmpty:{classList:classes},mediaArea:{classList:classes},enterTeachingStage(){}};
 vm.createContext(c);vm.runInContext(source.slice(source.indexOf('function restoreWorkedExample('),source.indexOf('function closeLessonMedia(')),c);
 const good={title:'Example',source:'Synthetic',steps:['One','Two'],index:1};c.restoreWorkedExample(good);assert.equal(renders,1);
 for(const bad of [null,{...good,index:4},{...good,steps:['']},{...good,steps:['x'.repeat(4001)]},{kind:'simulation',url:'https://example.invalid'}])c.restoreWorkedExample(bad);
 assert.equal(renders,1);
});
test('capturing an active example preserves the original lesson and active example context',()=>{
 const c=harness();const base=c.captureLessonCheckpoint();c.teachingStage={mode:'example',checkpoint:base};c.currentWorkedExample={title:'Example',source:'Synthetic',steps:['Example one','Example two']};c.mediaReplayPlayer={getStep:()=>({index:1,text:'Example two'})};
 const saved=c.captureLessonCheckpoint();assert.equal(saved.step,'Example two');assert.equal(saved.example.index,1);assert.equal(saved.steps[1],'Translated graph step');
 c.currentWorkedExample.steps[1]='Changed';assert.equal(saved.example.steps[1],'Example two');
});
function voiceHarness(){
 const calls=[];let resumed=0;
 const c={subjectClassroom:null,teachingStage:{mode:'example'},mediaReplayPlayer:{getStep:()=>({index:1,text:'Exact example step'})},lessonInterruption:null,lessonHistory:[],teacherSpeechPaused:false,currentLesson:{text:'Main lesson',index:0,steps:['Main lesson step']},stopTeacherAudio(){},lessonDirector:{classList:{remove(){}}},canvasStatus:{},setLearningStatus(){},renderCurrentLessonStep(){},speakText(...args){calls.push(args)},resumeTeacherAudio(){resumed++},restoreLessonCheckpoint(checkpoint){c.teachingStage.mode=checkpoint.example?'example':'lesson'},canvasAnswer:{innerText:'Main lesson'},showHandsFreeHeard(){},updateHandsFreeStatus(){}};
 vm.createContext(c);vm.runInContext(source.slice(source.indexOf('function resumeBookmarkedLessonByVoice('),source.indexOf('function setTeacherSpeechPace(')),c);
 return {c,calls,resumed:()=>resumed};
}
test('hands-free continue and repeat read the active example while preserving its stage',()=>{
 const h=voiceHarness();h.c.continueHandsFreeTeaching();h.c.replayCurrentTeachingAudio();assert.equal(h.calls.length,2);
 for(const call of h.calls){assert.equal(call[0],'Exact example step');assert.equal(call[2],false);assert.equal(call[3],true);}
 h.c.teacherSpeechPaused=true;h.c.continueHandsFreeTeaching();assert.equal(h.resumed(),1);assert.equal(h.calls.length,2);
});
test('voice replay reads the active subject answer before a saved Maths example',()=>{
 const h=voiceHarness();h.c.subjectClassroom={isOpen:()=>true,getAnswer:()=>'English explanation'};
 h.c.replayCurrentTeachingAudio();
 assert.equal(h.calls.length,1);assert.equal(h.calls[0][0],'English explanation');
 assert.equal(h.calls[0][2],false);assert.equal(h.calls[0][3],true);
});
test('voice replay does not fall back to Maths when the subject answer is unavailable',()=>{
 const h=voiceHarness();h.c.subjectClassroom={isOpen:()=>true,getAnswer:()=>''};
 h.c.replayCurrentTeachingAudio();assert.equal(h.calls.length,0);
});
test('voice return restores a pending example checkpoint before older history',()=>{
 const h=voiceHarness();h.c.teachingStage.mode='lesson';h.c.lessonInterruption={example:{index:1}};h.c.lessonHistory.push({text:'Older'});
 h.c.resumeBookmarkedLessonByVoice();assert.equal(h.c.lessonHistory.length,1);assert.equal(h.calls[0][0],'Exact example step');assert.equal(h.c.lessonInterruption,null);
});
test('next and previous voice intents move the active example instead of the main lesson',()=>{
 const moved=[];const c={teachingStage:{mode:'example'},mediaReplayPlayer:{moveBy:n=>moved.push(n)},teacherPanel:{classList:{contains:()=>false}},normalizeSpokenIntent:t=>t,updateHandsFreeStatus(){},currentLesson:{},moveLessonStep(){throw Error('Main lesson should not move')}};
 vm.createContext(c);vm.runInContext(source.slice(source.indexOf('function executeHandsFreeIntent('),source.indexOf('function handleHandsFreePhrase(')),c);
 c.executeHandsFreeIntent('next step');c.executeHandsFreeIntent('previous step');assert.deepEqual(moved,[1,-1]);
});
test('saved classroom snapshot retains an active example and clears it after leaving',()=>{
 let stored;let example={title:'Example',source:'Synthetic',steps:['First','Exact second'],index:1};
 const c={learnerNickname:{value:'SyntheticQA'},learnerCode:{value:'TEST-RECOVERY'},learnerClass:{value:'JSS2'},language:{value:'English'},currentLesson:{text:'Main lesson',steps:['Main step'],index:0},canvasAnswer:{innerText:'Main step'},lessonHistory:[],lessonInterruption:null,canvasStatus:{textContent:'Ready'},captureLessonCheckpoint:()=>({example}),localStorage:{setItem(k,v){stored=JSON.parse(v)}},refreshResumeLearning(){}};
 vm.createContext(c);vm.runInContext(source.slice(source.indexOf('function saveClassroomSnapshot('),source.indexOf('function clearClassroomSnapshot(')),c);
 c.saveClassroomSnapshot();assert.equal(stored.workedExample.index,1);assert.equal(stored.workedExample.steps[1],'Exact second');assert.equal(stored.answer,'Main lesson');
 example=null;c.saveClassroomSnapshot();assert.equal(stored.workedExample,null);
});

test('hands-free video questions capture the video before submitting chat',()=>{
 const calls=[];
 const c={
  teachingStage:{mode:'example'},mediaReplayPlayer:{getCheckpoint:()=>({id:'adding-directed-numbers',time:20})},
  teacherPanel:{classList:{contains:()=>false}},normalizeSpokenIntent:t=>t,currentLesson:{},
  lessonInterruption:null,handsFree:{},question:{},
  askTopicVideo(){calls.push('capture video');c.lessonInterruption={video:c.mediaReplayPlayer.getCheckpoint()};},
  pauseLessonForQuestion(){calls.push('pause lesson');},stopHandsFreeListening(){},
  form:{requestSubmit(){calls.push(['submit',c.question.value,c.lessonInterruption?.video]);}},
 };
 vm.createContext(c);vm.runInContext(source.slice(source.indexOf('function executeHandsFreeIntent('),source.indexOf('function handleHandsFreePhrase(')),c);
 c.executeHandsFreeIntent('Where did the dot land?');
 assert.deepEqual(calls,['capture video',['submit','Where did the dot land?',{id:'adding-directed-numbers',time:20}]]);
 assert.equal(c.handsFree.processing,true);
});

test('spoken video handoff closes the video before narrating the restored step',()=>{
 const calls=[];
 const c={
  normalizeSpokenIntent:value=>value,
  teachingStage:{mode:'example'},
  mediaReplayPlayer:{getCheckpoint:()=>({id:'adding-directed-numbers',time:20})},
  currentLesson:{steps:['Temporary example'],index:0},
  closeLessonMedia(){
   calls.push('close video');
   c.teachingStage.mode='lesson';
   c.currentLesson={steps:['Original lesson step'],index:0};
  },
  speakText(text){calls.push(text);},
  updateHandsFreeStatus(){},
  showHandsFreeHeard(text){calls.push(text);},
 };
 vm.createContext(c);
 vm.runInContext(source.slice(source.indexOf('function executeHandsFreeIntent('),source.indexOf('function handleHandsFreePhrase(')),c);
 vm.runInContext(source.slice(source.indexOf('function continueTeacherAfterVideo('),source.indexOf('function restoreTopicVideo(')),c);
 c.executeHandsFreeIntent('continue with the teacher');
 assert.deepEqual(calls,['close video','Original lesson step']);
 c.executeHandsFreeIntent('continue with teacher');
 assert.match(calls[2],/from a lesson video/);
 assert.equal(calls.length,3);
});

test('recognized wake phrase accepts the branded hyphen and repeated spaces',()=>{
 const calls=[];
 const c={handsFree:{},teacherSpeechPaused:false,showHandsFreeHeard(){},updateHandsFreeStatus(){},
  teachingStage:{mode:'example'},mediaReplayPlayer:{getCheckpoint(){}},
  continueTeacherAfterVideo(){calls.push('handoff');}};
 vm.createContext(c);
 vm.runInContext(source.slice(source.indexOf('function normalizeSpokenIntent('),source.indexOf('function clearHandsFreePhraseBuffer(')),c);
 vm.runInContext(source.slice(source.indexOf('function isSafeHandsFreeControl('),source.indexOf('function enableHandsFree(')),c);
 c.handleHandsFreePhrase('Robo-Teacher, continue  with the teacher.',.4);
 c.handleHandsFreePhrase('Robo Teacher, continue with teacher.',.9);
 assert.deepEqual(calls,['handoff','handoff']);
});
