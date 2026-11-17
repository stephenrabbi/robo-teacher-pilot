const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const src=fs.readFileSync('classroom/app.js','utf8');
function harness(){
 let buffers=0,cancelled=0,speaking=0;
 const context={currentTime:0,createBuffer(){buffers++;throw new Error('Stale audio scheduled');}};
 const ctx={teacherSpeechRequest:1,teacherStreamComplete:false,teacherSpeechPaused:false,teacherAudioSources:new Set(),prepareTeacherAudio:async()=>context,stopTeacherAudio(){},readAnswerButton:{},stopAudioKeepAlive(){},setTeacherSpeaking(){speaking++},Uint8Array,DataView};
 vm.createContext(ctx);
 vm.runInContext(src.slice(src.indexOf('async function playPcmStream('),src.indexOf('async function requestTeacherSpeech(')),ctx);
 return {ctx,counts:()=>({buffers,cancelled,speaking}),response(read){return {body:{getReader:()=>({read,cancel:async()=>{cancelled++}})}}}};
}
test('an interruption while waiting for a PCM chunk cannot restart speech',async()=>{
 const h=harness();let deliver,started;const reading=new Promise(resolve=>{started=resolve});
 const response=h.response(()=>new Promise(resolve=>{deliver=resolve;started()}));
 const pending=h.ctx.playPcmStream(response,1);
 await reading;h.ctx.teacherSpeechRequest=2;
 deliver({done:false,value:new Uint8Array([0,0])});await pending;
 assert.deepEqual(h.counts(),{buffers:0,cancelled:1,speaking:0});assert.equal(h.ctx.teacherStreamComplete,false);
});
test('an old stream cannot mark newer speech complete',async()=>{
 const h=harness();let deliver,started;const reading=new Promise(resolve=>{started=resolve});
 const pending=h.ctx.playPcmStream(h.response(()=>new Promise(resolve=>{deliver=resolve;started()})),1);
 await reading;h.ctx.teacherSpeechRequest=2;deliver({done:true});await pending;
 assert.equal(h.ctx.teacherStreamComplete,false);
});
test('cancellation during audio preparation does not consume the stream',async()=>{
 const h=harness();h.ctx.prepareTeacherAudio=async()=>{h.ctx.teacherSpeechRequest=2;return {}};
 await h.ctx.playPcmStream(h.response(()=>{throw new Error('Must not read')}),1);
 assert.equal(h.ctx.teacherStreamComplete,false);
});
test('example narration keeps the stage open while normal lesson reading returns to the lesson',async()=>{
 for(const keepOpen of [true,false]){
  let closed=0,restored=0,played=0,payload;
  const ctx={currentLesson:null,subjectClassroom:null,mathsNarrationSettings:()=> 'Yoruba:female:normal',teachingStage:{mode:'example'},lessonController:{begin(){}},stopLessonMedia(){closed++},restoreTeachingStage(){restored++},stopTeacherAudio(){},setCanvasVoiceAvatar(){},teacherVoiceStatus:{},readAnswerButton:{setAttribute(){}},setLearningStatus(){},teacherSpeechRequest:1,teacherSpeechController:null,AbortController,startAudioKeepAlive:async()=>{},ensureSession:async()=> 'synthetic',prepareSpeechText:t=>t,language:{value:'Yoruba'},teacherPanel:{dataset:{voiceGender:'female'}},teacherSpeechPace:1,requestTeacherSpeech:async p=>{payload=p;return {ok:true,status:200,body:{}}},playPcmStream:async()=>{played++},addMessage(){throw Error('Unexpected speech failure')}};
  vm.createContext(ctx);vm.runInContext(src.slice(src.indexOf('async function speakText('),src.indexOf("readAnswerButton.addEventListener('click'")),ctx);
  await ctx.speakText('Current example step',false,false,keepOpen);
  assert.equal(played,1);assert.equal(closed,keepOpen?0:1);assert.equal(restored,keepOpen?0:1);
  assert.equal(payload.text,'Current example step');assert.equal(payload.language,'Yoruba');
 }
});

test('complete Maths narration resumes from the original buffer offset',async()=>{
 const lesson={index:1};
 const first={duration:2},second={duration:3};
 const checkpoint={};
 const starts=[];
 const context={state:'running',currentTime:11,createBufferSource(){
  return {connect(){},addEventListener(){},start(time,offset){starts.push([this.buffer,time,offset]);}};
 }};
 const ctx={activeMathsNarration:{lesson,index:1,settings:'English:female:normal',chunks:[
  {buffer:first,start:10,offset:0},{buffer:second,start:12,offset:0},
 ]},currentLesson:lesson,teacherStreamComplete:false,teacherAudioContext:context,
 teachingStage:{mode:'lesson'},mathsNarrationCheckpoints:new Map(),language:{value:'English'},
 teacherPanel:{dataset:{voiceGender:'female'}},teacherSpeechPace:'normal',teacherSpeechRequest:1,
 prepareTeacherAudio:async()=>context,ensureAvatarAnalyser(){},teacherAudioSources:new Set(),
 lessonController:{begin(){}},setCanvasVoiceAvatar(){},readAnswerButton:{},setTeacherSpeaking(){},
 speakText(){throw Error('The buffered narration should not request fresh speech');}};
 vm.createContext(ctx);
 vm.runInContext(src.slice(src.indexOf('function rememberMathsNarration('),src.indexOf('async function playPcmStream(')),ctx);
 ctx.rememberMathsNarration(checkpoint);
 assert.equal(ctx.mathsNarrationCheckpoints.size,0);
 ctx.teacherStreamComplete=true;
 ctx.rememberMathsNarration(checkpoint);
 context.currentTime=30;
 await ctx.resumeMathsNarration(checkpoint,'Saved step');
 assert.deepEqual(starts,[[first,30.06,1],[second,31.06,0]]);
 assert.equal(ctx.mathsNarrationCheckpoints.size,0);
});

test('mouth cues follow buffered audio offsets and stay closed in playback gaps',()=>{
 const ctx={};
 vm.createContext(ctx);
 vm.runInContext(src.slice(src.indexOf('const mathsMouthShapes='),src.indexOf('function renderMathsMouthCue(')),ctx);
 const cues=ctx.parseMathsMouthCues(JSON.stringify([
  {start:0,end:1,value:'A'},{start:1,end:2,value:'F'},{start:2,end:3,value:'E'}
 ]));
 assert.equal(cues.length,3);
 assert.equal(ctx.parseMathsMouthCues('[{"start":0,"end":1,"value":"__proto__"}]'),null);
 assert.equal(ctx.parseMathsMouthCues('[{"start":0,"end":2,"value":"F"},{"start":1,"end":3,"value":"E"}]'),null);
 const narration={cues,chunks:[{start:20,timeline:1,offset:.5,buffer:{duration:2}}]};
 assert.equal(ctx.mathsMouthCueAt(narration,19.9),'X');
 assert.equal(ctx.mathsMouthCueAt(narration,20.25),'F');
 assert.equal(ctx.mathsMouthCueAt(narration,20.75),'E');
 assert.equal(ctx.mathsMouthCueAt(narration,21.5),'X');
 assert.equal(ctx.mathsMouthCueAt({chunks:[]},20),null);
});

test('a failed mouth image can be retried on the next narration',()=>{
 const images=[];
 class FakeImage {
  constructor(){images.push(this);}
  addEventListener(event,handler){assert.equal(event,'error');this.fail=handler;}
 }
 const ctx={Image:FakeImage};
 vm.createContext(ctx);
 vm.runInContext(src.slice(src.indexOf('const mathsMouthShapes='),src.indexOf('function renderMathsMouthCue(')),ctx);
 ctx.prepareMathsMouthImages([{value:'B'},{value:'G'}]);
 assert.equal(images.length,1);
 images[0].fail();
 ctx.prepareMathsMouthImages([{value:'B'}]);
 ctx.prepareMathsMouthImages([{value:'B'}]);
 assert.equal(images.length,2);
 assert.equal(images[1].src,images[0].src);
});

test('Continue replays the same Maths step when a closed context held an incomplete stream',async()=>{
 const lesson={index:1,steps:['Identify the equation.','Add two to both sides.']};
 const requests=[];
 const ctx={
  currentLesson:lesson,
  activeMathsNarration:{lesson,index:1,chunks:[{buffer:{duration:1},start:0,offset:0}]},
  teacherAudioContext:{state:'closed',currentTime:.25},
  teacherSpeechPaused:true,
  teacherStreamComplete:false,
  teachingStage:{mode:'lesson'},
  mathsNarrationCheckpoints:new Map(),
  stopTeacherAudio(){ctx.teacherSpeechPaused=false;ctx.activeMathsNarration=null;},
  speakText:async (...args)=>requests.push(args),
 };
 vm.createContext(ctx);
 vm.runInContext(src.slice(src.indexOf('async function resumeTeacherAudio('),src.indexOf('function stopAudioKeepAlive(')),ctx);
 vm.runInContext(src.slice(src.indexOf('function rememberMathsNarration('),src.indexOf('async function playPcmStream(')),ctx);
 await ctx.resumeTeacherAudio();
 assert.deepEqual(requests,[['Add two to both sides.',true,true]]);
 assert.equal(lesson.index,1);
 assert.equal(ctx.teacherSpeechPaused,false);
 assert.equal(ctx.mathsNarrationCheckpoints.size,0);
});

test('an old Continue request cannot change the new lesson audio state',async()=>{
 for(const fails of [false,true]){
  let finishResume;
  const changes=[];
  const ctx={
   activeMathsNarration:null,
   teacherSpeechRequest:1,
   teacherSpeechPaused:true,
   teacherAudioContext:{state:'running',resume:()=>new Promise((resolve,reject)=>{
    finishResume=()=>fails?reject(new Error('Old audio failed')):resolve();
   })},
   lessonController:{begin(){changes.push('begin');}},
   setTeacherSpeaking(){changes.push('speaking');},
   stopTeacherAudio(){changes.push('stop');},
   addMessage(){changes.push('error');},
  };
  vm.createContext(ctx);
  vm.runInContext(src.slice(src.indexOf('async function resumeTeacherAudio('),src.indexOf('function stopAudioKeepAlive(')),ctx);
  const pending=ctx.resumeTeacherAudio();
  ctx.teacherSpeechRequest++;
  finishResume();
  await pending;
  assert.deepEqual(changes,[]);
  assert.equal(ctx.teacherSpeechPaused,true);
 }
});

test('a failed Pause restores speaking only for the narration that requested it',async()=>{
 for(const replaced of [false,true]){
  let failPause;
  const speaking=[];
  const ctx={
   teacherSpeechRequest:1,teacherSpeechPaused:false,
   teacherAudioContext:{suspend:()=>new Promise((_,reject)=>{failPause=reject;})},
   lessonController:{begin(){}},teacherPanel:{classList:{add(){},remove(){}}},
   teacherVoiceStatus:{},syncMathsStepPointing(){},showVoiceAnswerAvatar:false,
   stopAvatarMotion(){},readAnswerButton:{setAttribute(){}},setLearningStatus(){},
   setTeacherSpeaking(value){speaking.push(value);},
  };
  vm.createContext(ctx);
  vm.runInContext(src.slice(src.indexOf('async function pauseTeacherAudio('),src.indexOf('async function resumeTeacherAudio(')),ctx);
  const pending=ctx.pauseTeacherAudio();
  assert.equal(ctx.teacherSpeechPaused,true);
  if(replaced)ctx.teacherSpeechRequest++;
  failPause(new Error('Audio suspend failed'));
  await pending;
  assert.deepEqual(speaking,replaced?[]:[true]);
  assert.equal(ctx.teacherSpeechPaused,replaced);
 }
});

test('Read answer checks playback ownership after the audio context is ready',async()=>{
 for(const change of ['none','request','workspace','answer']){
  let click,finishPreparation;
  let subjectOpen=false;
  const spoken=[];
  const ctx={
   teacherSpeechRequest:1,teacherSpeechPaused:false,
   teacherPanel:{classList:{contains:()=>false}},
   readAnswerButton:{addEventListener(_event,handler){click=handler;}},
   subjectClassroom:{isOpen:()=>subjectOpen,getAnswer:()=>'English explanation'},
   canvasAnswer:{textContent:'Original Maths step'},
   prepareTeacherAudio:()=>new Promise(resolve=>{finishPreparation=resolve;}),
   speakText(...args){spoken.push(args);},
  };
  vm.createContext(ctx);
  vm.runInContext(src.slice(src.indexOf("readAnswerButton.addEventListener('click'"),src.indexOf('teacherSpeed.value=teacherSpeechPace;',src.indexOf("readAnswerButton.addEventListener('click'"))),ctx);
  const pending=click();
  if(change==='request')ctx.teacherSpeechRequest++;
  if(change==='workspace')subjectOpen=true;
  if(change==='answer')ctx.canvasAnswer.textContent='Different Maths step';
  finishPreparation();
  await pending;
  assert.deepEqual(spoken,change==='none'?[['Original Maths step',false,true,true]]:[]);
 }
});
