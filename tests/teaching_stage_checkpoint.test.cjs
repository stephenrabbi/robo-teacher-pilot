const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const src=fs.readFileSync('classroom/app.js','utf8');
function harness(){
 const hidden={add(){},remove(){}};
 const ctx={currentLesson:{text:'Original lesson',index:1,steps:['Introduction','Exact translated step','Check']},teachingStage:{mode:'lesson',checkpoint:null,lesson:null},canvasWork:{classList:hidden},canvasEmpty:{classList:hidden},canvasAnswer:{textContent:''},setTeachingStageMode(mode){ctx.teachingStage.mode=mode},setCanvasVoiceAvatar(){},saveClassroomSnapshot(){},setTeacherPanelMinimized(){},renderCurrentLessonStep(){},restoreTeacherPanel(){},setLearningStatus(){},startLessonDirector(text,index,steps){ctx.currentLesson={text,index,steps:steps.slice()}}};
 vm.createContext(ctx);
 vm.runInContext(src.slice(src.indexOf('function captureLessonCheckpoint('),src.indexOf('function restoreLessonHistory(')),ctx);
 vm.runInContext(src.slice(src.indexOf('function enterTeachingStage('),src.indexOf('function renderCurrentLessonStep(')),ctx);
 return ctx;
}
test('visual return restores the exact original steps and position',()=>{
 const c=harness();c.enterTeachingStage('visual');c.currentLesson.steps[1]='Changed by another activity';c.currentLesson.index=2;
 c.restoreTeachingStage();assert.equal(c.currentLesson.index,1);assert.equal(c.currentLesson.steps[1],'Exact translated step');assert.equal(c.teachingStage.checkpoint,null);
});
test('switching between example and visual retains the original return point',()=>{
 const c=harness();c.enterTeachingStage('example');c.currentLesson.index=2;c.enterTeachingStage('visual');c.restoreTeachingStage();assert.equal(c.currentLesson.index,1);
});
test('closing an obsolete stage cannot overwrite a newer lesson',()=>{
 const c=harness();c.enterTeachingStage('visual');c.currentLesson={text:'New lesson',index:0,steps:['New explanation']};c.restoreTeachingStage();assert.equal(c.currentLesson.text,'New lesson');assert.equal(c.currentLesson.index,0);
});
test('closing a stage after learner reset does not resurrect the old lesson',()=>{
 const c=harness();c.enterTeachingStage('example');c.currentLesson=null;c.restoreTeachingStage();assert.equal(c.currentLesson,null);assert.equal(c.teachingStage.checkpoint,null);
});
test('return does not restart the director and replay automatic teaching stages',()=>{
 const c=harness();c.startLessonDirector=()=>{throw new Error('Must retain existing choreography state')};
 c.enterTeachingStage('visual');assert.doesNotThrow(()=>c.restoreTeachingStage());assert.equal(c.currentLesson.index,1);
});
