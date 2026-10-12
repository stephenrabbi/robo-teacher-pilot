// Synthetic, offline contract tests. NO real learner data or Supabase credentials.
// Run: node tests/supabase_identity_adapter_contract.cjs
const assert = require("node:assert/strict");
const adapter = require("../classroom/supabase-identity-gated.js");

(async () => {
  let authCalls = 0, dbCalls = 0;
  const fake = {
    auth: { async getUser() { authCalls++; return {data:{user:{id:"synthetic-A"}}}; } },
    from() { dbCalls++; throw Error("Disabled adapter must not access database"); }
  };
  const client = adapter.createAdapter(fake,{enabled:true});
  assert.equal(adapter.ENABLED,false,"Feature flag must remain off");
  assert.equal(client.enabled,false,"External options cannot override internal OFF switch");
  assert.deepEqual(await client.readOwnProgress(),{enabled:false,rows:[]});
  assert.deepEqual(await client.readOwnProfile(),{enabled:false,profile:null});
  assert.equal(await client.verifiedUser(),null);
  assert.equal(authCalls,0);
  assert.equal(dbCalls,0);
  assert.throws(()=>adapter.createAdapter({}),/Supabase auth client required/);
  console.log("PASS: Supabase identity adapter is fail-closed; no auth or DB calls when disabled.");
})().catch(e=>{console.error(e);process.exitCode=1;});
