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
