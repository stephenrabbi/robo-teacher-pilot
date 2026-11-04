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

test('expired media session renews once using the new token',async()=>{
 const h=harness();h.ctx.sessionToken='expired';let attempts=0;const tokens=[];
 h.ctx.ensureSession=async()=>h.ctx.sessionToken||(h.ctx.sessionToken='renewed');
 h.ctx.fetch=async(_url,options)=>{tokens.push(JSON.parse(options.body).session_token);return ++attempts===1?{status:401,ok:false}:ok};
 await h.ctx.openLessonMedia();assert.deepEqual(tokens,['expired','renewed']);assert.equal(h.counts().rendered,1);
});
test('a repeated unauthorized response stops after one retry',async()=>{
 const h=harness();h.ctx.sessionToken='synthetic';let attempts=0;
 h.ctx.fetch=async()=>{attempts++;return {status:401,ok:false,json:async()=>({detail:'expired'})}};
 await h.ctx.openLessonMedia();assert.equal(attempts,2);assert.equal(h.counts().messages,1);
});
function catalogueHarness(){
 const h=harness();const scripts=[];let timer;
 h.ctx.window={RoboTeacherVideos:{getTopicVideo:()=>null}};
 h.ctx.clearTimeout=()=>{};h.ctx.setTimeout=fn=>{timer=fn;return 1};
 h.ctx.document={createElement:()=>({remove(){this.removed=true}}),head:{appendChild:script=>scripts.push(script)}};
 return {...h,scripts,timeout:()=>timer()};
}
test('missing catalogue refresh is shared and loads only a fixed same-origin script',async()=>{
 const h=catalogueHarness();const a=h.ctx.ensureTopicVideoCatalogue('adding-unlike-fractions');const b=h.ctx.ensureTopicVideoCatalogue('adding-unlike-fractions');
 assert.equal(h.scripts.length,1);assert.match(h.scripts[0].src,/^\/classroom\/topic_video\.js\?refresh=\d+$/);
 h.ctx.window.RoboTeacherVideos.getTopicVideo=()=>({id:'adding-unlike-fractions'});h.scripts[0].onload();
 assert.equal(await a,true);assert.equal(await b,true);assert.equal(h.scripts[0].removed,true);
});
test('catalogue failure and timeout are bounded and invalid IDs never load scripts',async()=>{
 const h=catalogueHarness();assert.equal(await h.ctx.ensureTopicVideoCatalogue('https://other/script'),false);assert.equal(h.scripts.length,0);
 const failed=h.ctx.ensureTopicVideoCatalogue('missing');h.scripts[0].onerror();assert.equal(await failed,false);
 const timed=h.ctx.ensureTopicVideoCatalogue('missing');h.timeout();assert.equal(await timed,false);assert.equal(h.scripts.length,2);
});
test('a question during catalogue refresh prevents an obsolete video opening',async()=>{
 const h=catalogueHarness();h.ctx.fetch=async()=>({ok:true,json:async()=>({kind:'video',video_id:'adding-unlike-fractions'})});
 const pending=h.ctx.openLessonMedia();while(!h.scripts.length)await Promise.resolve();
 h.ctx.lessonController.begin('question');h.ctx.window.RoboTeacherVideos.getTopicVideo=()=>({});h.scripts[0].onload();await pending;
 assert.equal(h.counts().rendered,0);assert.equal(h.counts().messages,0);
});
