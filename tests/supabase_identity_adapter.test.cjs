/* Standalone safety regression tests: node tests/supabase_identity_adapter.test.cjs
 * Uses synthetic mocks only. Does not create Supabase users or touch live data.
 */
const assert=require("node:assert/strict");
const adapter=require("../classroom/supabase-identity-gated.js");
async function run(){
  let authCalls=0,queryCalls=0;
  const client={
    auth:{getUser:async()=>{authCalls++;return {data:{user:{id:"00000000-0000-4000-8000-000000000001"}}}}},
    from:()=>{queryCalls++;throw Error("Cloud read should never occur with flag disabled")}
  };
  assert.equal(adapter.ENABLED,false,"Production integration must remain hard-disabled");
  const source=adapter.createAdapter(client,{enabled:true});
  assert.equal(source.enabled,false,"Caller must not override internal safety gate");
  assert.equal(await source.verifiedUser(),null);
  assert.deepEqual(await source.readOwnProgress(),{enabled:false,rows:[]});
  assert.deepEqual(await source.readOwnProfile(),{enabled:false,profile:null});
  assert.equal(authCalls,0);
  assert.equal(queryCalls,0);
  assert.throws(()=>adapter.createAdapter({auth:{}}),/getUser/);
  assert.equal(typeof source.writeProgress,"undefined","Direct learner writes must not be exposed");
  assert.equal(typeof source.claimLearnerCode,"undefined","Codes must not be identity proof");
  console.log("PASS: Supabase adapter remains disabled; no auth, read or write calls");
}
run().catch(e=>{console.error(e);process.exitCode=1});
