const test=require('node:test');
const assert=require('node:assert/strict');
const {createSessionController}=require('../progress_store/session_queue_controller.cjs');
function store(){const m=new Map();return{getItem:k=>m.get(k)??null,setItem:(k,v)=>m.set(k,v)}}
const session=(subject)=>({scope:{school:'demo',subject},token:'synthetic-token-'+subject});
const event=id=>({event_id:id,topic_key:'fractions'});
test('logout blocks uploads and enqueues until another session is selected',async()=>{
  const controller=createSessionController(store());
  controller.switchSession(session('A'));
  controller.queue(event('a1'));
  controller.switchSession(null);
  assert.equal(controller.current(),null);
  assert.throws(()=>controller.queue(event('a2')),/No active session/);
  await assert.rejects(controller.flush(async()=>true),/No active session/);
});
test('session switch prevents next queued event from being submitted',async()=>{
  const controller=createSessionController(store());
  controller.switchSession(session('A'));
  controller.queue(event('a1'));controller.queue(event('a2'));
  const seen=[];
  const result=await controller.flush(async (payload, token)=>{
    seen.push([payload.event_id,token]);
    controller.switchSession(session('B'));
    return true;
  });
  assert.deepEqual(seen,[['a1','synthetic-token-A']]);
  assert.equal(result.synchronized,false);
  controller.switchSession(session('A'));
  const remaining=await controller.flush(async x=>{seen.push([x.event_id,'retry']);return true});
  assert.equal(remaining.pending,0);
  assert.deepEqual(seen.map(x=>x[0]),['a1','a2']);
});
test('different learner pending progress cannot be flushed through another session',async()=>{
  const controller=createSessionController(store());
  controller.switchSession(session('A'));
  controller.queue(event('a1'));
  controller.switchSession(session('B'));
  const result=await controller.flush(async()=>{throw Error('should not upload A')});
  assert.equal(result.pending,0);
  controller.switchSession(session('A'));
  assert.equal((await controller.flush(async()=>true)).acknowledged,1);
});
test('malformed session cannot become active',()=>{
  const controller=createSessionController(store());
  assert.throws(()=>controller.switchSession({scope:{school:'demo'},token:'fake'}),/session|scope/);
});
