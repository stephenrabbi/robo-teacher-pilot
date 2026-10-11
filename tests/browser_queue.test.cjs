const test = require('node:test');
const assert = require('node:assert/strict');
const sync = require('../progress_store/browser_queue.cjs');
function storage() {
  const m = new Map();
  return {getItem:k=>m.has(k)?m.get(k):null,setItem:(k,v)=>m.set(k,v)};
}
const ev = id => ({event_id:id,correct:3,total:5});

test('pending event remains stored until server acknowledges', async () => {
  const s=storage();
  sync.enqueue(s,ev('one'));
  assert.equal(sync.read(s).length,1);
  let result=await sync.flush(s,async()=>{throw Error('offline')});
  assert.deepEqual(result,{acknowledged:0,pending:1,synchronized:false});
  result=await sync.flush(s,async()=>true);
  assert.equal(result.pending,0);
});
test('idempotent already-saved response clears duplicate', async () => {
  const s=storage();sync.enqueue(s,ev('one'));sync.enqueue(s,ev('one'));
  assert.equal(sync.read(s).length,1);
  assert.equal((await sync.flush(s,async()=>false)).pending,0);
});
test('uncertain response keeps progress', async () => {
  const s=storage();sync.enqueue(s,ev('one'));
  assert.equal((await sync.flush(s,async()=>undefined)).pending,1);
});
test('invalid storage cannot erase unsent progress', () => {
  const s=storage();s.setItem(sync.STORAGE_KEY,'{corrupt');
  assert.throws(()=>sync.enqueue(s,ev('one')),/recovery/);
  assert.equal(s.getItem(sync.STORAGE_KEY),'{corrupt');
});
test('conflicting IDs do not overwrite existing progress', () => {
  const s=storage();sync.enqueue(s,ev('one'));
  assert.throws(()=>sync.enqueue(s,{...ev('one'),correct:4}),/Conflicting/);
  assert.equal(sync.read(s)[0].event.correct,3);
});
