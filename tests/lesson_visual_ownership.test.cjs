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
 const ctx={currentLesson:{text:'Original lesson',index:1},canvasAnswer:{textContent:''},lessonController:createLessonController(),visualButton:{},language:{value:'English'},ensureSession:async()=> 'synthetic',stopTeacherAudio(){},setLearningStatus(){},addMessage(){messages++},fetch:()=>{fetches++;started();return response},dismissLessonOverlays(){},renderVisualAid(){rendered++},canvasWork:{classList:classes()},canvasEmpty:{classList:classes()},visualArea:{classList:classes()},enterTeachingStage(){},setTimeout,Promise};
 vm.createContext(ctx);vm.runInContext(src.slice(src.indexOf('let visualPreparationRequest='),src.indexOf('function renderVisualAid(')),ctx);
 return {ctx,resolve,reject,fetched,counts:()=>({rendered,messages,fetches})};
}
const ok={ok:true,json:async()=>({title:'Synthetic diagram'})};
test('a late visual cannot replace a learner question',async()=>{
 const h=harness();const pending=h.ctx.showVisualExplanation();await h.fetched;
 h.ctx.lessonController.begin('question');h.resolve(ok);await pending;
 assert.equal(h.counts().rendered,0);assert.equal(h.ctx.visualButton.disabled,false);
});
test('an obsolete visual failure does not replace current feedback',async()=>{
 const h=harness();const pending=h.ctx.showVisualExplanation();await h.fetched;
 h.ctx.lessonController.begin('lesson');h.reject(new Error('old request'));await pending;
 assert.equal(h.counts().messages,0);
});
test('the current visual still renders normally',async()=>{
 const h=harness();const pending=h.ctx.showVisualExplanation();await h.fetched;h.resolve(ok);await pending;
 assert.equal(h.counts().rendered,1);assert.equal(h.ctx.visualButton.disabled,false);
});
test('interruption during session preparation avoids a visual request',async()=>{
 const h=harness();h.ctx.ensureSession=async()=>{h.ctx.lessonController.begin('question');return 'synthetic'};
 await h.ctx.showVisualExplanation();assert.equal(h.counts().fetches,0);
});
test('automatic and manual panel transitions keep accessible labels consistent',()=>{
 const ctx={teacherPanel:{classList:classes()},classroom:{classList:classes()},toggle:{setAttribute(k,v){this[k]=v}}};vm.createContext(ctx);
 vm.runInContext(src.slice(src.indexOf('function setTeacherPanelMinimized('),src.indexOf('function prepareSpeechText(')),ctx);
 ctx.setTeacherPanelMinimized(true);assert.equal(ctx.toggle['aria-label'],'Maximize teacher');assert.equal(ctx.toggle['aria-expanded'],'false');assert.equal(ctx.classroom.classList.contains('teacher-min'),true);
 ctx.setTeacherPanelMinimized(false);assert.equal(ctx.toggle['aria-label'],'Minimize teacher');assert.equal(ctx.toggle['aria-expanded'],'true');assert.equal(ctx.teacherPanel.classList.contains('minimized'),false);
});
