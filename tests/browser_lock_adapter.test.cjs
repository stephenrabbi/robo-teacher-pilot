const test=require('node:test');
const assert=require('node:assert/strict');
const {createBrowserCrossTabSync}=require('../progress_store/browser_lock_adapter.cjs');
const mem=()=>{const m=new Map();return {getItem:k=>m.get(k)??null,setItem:(k,v)=>m.set(k,v)}};
const locks=()=>{let tail=Promise.resolve();return {request:(name,opts,fn)=>{assert.equal(opts.mode,'exclusive');const p=tail.then(fn);tail=p.catch(()=>{});return p}}};
const scope={school:'demo-school',subject:'learner-A'};
test('browser adapter refuses unavailable Web Locks',()=>{
 assert.throws(()=>createBrowserCrossTabSync({storage:mem(),scope,navigatorObject:{}}),/unavailable/);
});
test('browser adapter shares pending work across two tabs',async()=>{
 const storage=mem(),navigatorObject={locks:locks()};
 const tab1=createBrowserCrossTabSync({storage,scope,navigatorObject});
 const tab2=createBrowserCrossTabSync({storage,scope,navigatorObject});
 tab1.queue({event_id:'event-1',correct:2,total:3});let submitted=0;
 await Promise.all([tab1.flush(async()=>{submitted++;return true}),tab2.flush(async()=>{submitted++;return true})]);
 assert.equal(submitted,1);assert.equal(tab1.pending(),0);
});
test('adapter retries after failed network request',async()=>{
 const storage=mem(),navigatorObject={locks:locks()};
 const tab=createBrowserCrossTabSync({storage,scope,navigatorObject});
 tab.queue({event_id:'event-1'});
 assert.equal((await tab.flush(async()=>{throw Error('offline')})).pending,1);
 assert.equal((await tab.flush(async()=>true)).pending,0);
});
