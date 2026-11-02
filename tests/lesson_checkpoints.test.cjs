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
