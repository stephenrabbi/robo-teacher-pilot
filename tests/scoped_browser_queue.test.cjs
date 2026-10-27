const test=require('node:test');
const assert=require('node:assert/strict');
const sync=require('../progress_store/scoped_browser_queue.cjs');
function store(){let m=new Map();return{getItem:k=>m.get(k)||null,setItem:(k,v)=>m.set(k,v)}}
const a={school:'demo-school',subject:'learner-A'};
const b={school:'demo-school',subject:'learner-B'};
const item=id=>({event_id:id,correct:3,total:5});
test('two learners sharing a browser have separate pending queues',()=>{
 const s=store();sync.queue(s,a,item('event-a'));
 assert.equal(sync.pending(s,a),1);assert.equal(sync.pending(s,b),0);
 sync.queue(s,b,item('event-b'));assert.equal(sync.pending(s,b),1);
 assert.equal(sync.pending(s,a),1);
});
test('simultaneous flushes for same learner share one upload',async()=>{
 const s=store();sync.queue(s,a,item('one'));
 let calls=0;const send=async()=>{calls++;await new Promise(r=>setTimeout(r,5));return true};
 const [x,y]=await Promise.all([sync.flush(s,a,send),sync.flush(s,a,send)]);
 assert.equal(calls,1);assert.deepEqual(x,y);assert.equal(sync.pending(s,a),0);
});
test('offline failure keeps pending and releases retry lock',async()=>{
 const s=store();sync.queue(s,a,item('one'));
 const failed=await sync.flush(s,a,async()=>{throw Error('offline')});
 assert.equal(failed.synchronized,false);assert.equal(sync.pending(s,a),1);
 const retried=await sync.flush(s,a,async()=>true);
 assert.equal(retried.synchronized,true);assert.equal(sync.pending(s,a),0);
});
test('untrusted or missing scope rejected',()=>{
 const s=store();
 for(const scope of [{school:'x',subject:'../../other'},null,{school:'x'}])
   assert.throws(()=>sync.queue(s,scope,item('one')),/scope/);
});
