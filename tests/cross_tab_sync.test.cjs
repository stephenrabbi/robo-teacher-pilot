const test=require('node:test');
const assert=require('node:assert/strict');
const {createCrossTabSync}=require('../progress_store/cross_tab_sync.cjs');
function storage(){const m=new Map();return {getItem:k=>m.get(k)??null,setItem:(k,v)=>m.set(k,v)}}
function locks(){let tail=Promise.resolve();return {request:(_key,options,fn)=>{const current=tail.then(fn);tail=current.catch(()=>{});return current}}}
const scope={school:'synthetic-school',subject:'synthetic-learner'};
const event=id=>({event_id:id,correct:2,total:3});
test('two simulated tabs upload one event only once',async()=>{
 const s=storage(),l=locks();
 const a=createCrossTabSync({storage:s,locks:l,scope}),b=createCrossTabSync({storage:s,locks:l,scope});
 a.queue(event('event-1'));let calls=0;
 const upload=async()=>{calls++;await new Promise(resolve=>setTimeout(resolve,5));return true};
 await Promise.all([a.flush(upload),b.flush(upload)]);
 assert.equal(calls,1);assert.equal(a.pending(),0);assert.equal(b.pending(),0);
});
test('offline error retains pending across tabs',async()=>{
 const s=storage(),l=locks();
 const a=createCrossTabSync({storage:s,locks:l,scope}),b=createCrossTabSync({storage:s,locks:l,scope});
 a.queue(event('event-1'));
 assert.equal((await a.flush(async()=>{throw Error('offline')})).pending,1);
 assert.equal((await b.flush(async()=>true)).pending,0);
});
test('missing cross-tab locking refuses to sync',()=>{
 assert.throws(()=>createCrossTabSync({storage:storage(),scope}),/lock provider/);
});
