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
 const c={teachingStage:{mode:'example'},mediaReplayPlayer:{getStep:()=>({index:1,text:'Exact example step'})},lessonInterruption:null,lessonHistory:[],teacherSpeechPaused:false,currentLesson:{text:'Main lesson',index:0,steps:['Main lesson step']},stopTeacherAudio(){},lessonDirector:{classList:{remove(){}}},canvasStatus:{},setLearningStatus(){},renderCurrentLessonStep(){},speakText(...args){calls.push(args)},resumeTeacherAudio(){resumed++},restoreLessonCheckpoint(checkpoint){c.teachingStage.mode=checkpoint.example?'example':'lesson'},canvasAnswer:{innerText:'Main lesson'},showHandsFreeHeard(){},updateHandsFreeStatus(){}};
 vm.createContext(c);vm.runInContext(source.slice(source.indexOf('function resumeBookmarkedLessonByVoice('),source.indexOf('function setTeacherSpeechPace(')),c);
 return {c,calls,resumed:()=>resumed};
}
test('hands-free continue and repeat read the active example while preserving its stage',()=>{
 const h=voiceHarness();h.c.continueHandsFreeTeaching();h.c.replayCurrentTeachingAudio();assert.equal(h.calls.length,2);
 for(const call of h.calls){assert.equal(call[0],'Exact example step');assert.equal(call[2],false);assert.equal(call[3],true);}
 h.c.teacherSpeechPaused=true;h.c.continueHandsFreeTeaching();assert.equal(h.resumed(),1);assert.equal(h.calls.length,2);
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
