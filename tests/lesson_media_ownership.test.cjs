const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {createLessonController}=require('../classroom/lesson_controller.js');
const src=fs.readFileSync('classroom/app.js','utf8');
function classes(){const set=new Set();return {toggle(k,v){v?set.add(k):set.delete(k)},contains:k=>set.has(k),add:k=>set.add(k),remove:k=>set.delete(k)}}
function harness(){
 let rendered=0,messages=0,resolve,reject,fetches=0,started;
 const fetched=new Promise(r=>{started=r});
 const response=new Promise((a,b)=>{resolve=a;reject=b});
 const ctx={currentLesson:{text:'Original lesson',index:1},canvasAnswer:{textContent:'',querySelectorAll:()=>[]},lessonController:createLessonController(),mediaButton:{},language:{value:'English'},ensureSession:async()=> 'synthetic',stopTeacherAudio(){},setLearningStatus(){},addMessage(){messages++},fetch:()=>{fetches++;started();return response},dismissLessonOverlays(){},renderLessonMedia(){rendered++},canvasWork:{classList:classes()},canvasEmpty:{classList:classes()},mediaArea:{classList:classes()},enterTeachingStage(){},setTimeout,Promise};
 vm.createContext(ctx);vm.runInContext(src.slice(src.indexOf('let mediaPreparationRequest='),src.indexOf('function renderLessonMedia(')),ctx);
 return {ctx,resolve,reject,fetched,counts:()=>({rendered,messages,fetches})};
}
const ok={ok:true,json:async()=>({title:'Synthetic diagram'})};
test('a late media cannot replace a learner question',async()=>{
 const h=harness();const pending=h.ctx.openLessonMedia();await h.fetched;
 h.ctx.lessonController.begin('question');h.resolve(ok);await pending;
 assert.equal(h.counts().rendered,0);assert.equal(h.ctx.mediaButton.disabled,false);
});
test('an obsolete media failure does not replace current feedback',async()=>{
 const h=harness();const pending=h.ctx.openLessonMedia();await h.fetched;
 h.ctx.lessonController.begin('lesson');h.reject(new Error('old request'));await pending;
 assert.equal(h.counts().messages,0);
});
test('the current media still renders normally',async()=>{
 const h=harness();const pending=h.ctx.openLessonMedia();await h.fetched;h.resolve(ok);await pending;
 assert.equal(h.counts().rendered,1);assert.equal(h.ctx.mediaButton.disabled,false);
});
test('interruption during session preparation avoids a media request',async()=>{
 const h=harness();h.ctx.ensureSession=async()=>{h.ctx.lessonController.begin('question');return 'synthetic'};
 await h.ctx.openLessonMedia();assert.equal(h.counts().fetches,0);
});

test('an obsolete finalizer cannot enable the button for a newer example',async()=>{
 const h=harness();const old=h.ctx.openLessonMedia();await h.fetched;
 let resolveNew;h.ctx.fetch=()=>new Promise(r=>{resolveNew=r});
 const latest=h.ctx.openLessonMedia();await Promise.resolve();
 h.resolve(ok);await old;assert.equal(h.ctx.mediaButton.disabled,true);
 resolveNew(ok);await latest;assert.equal(h.ctx.mediaButton.disabled,false);assert.equal(h.counts().rendered,1);
});
