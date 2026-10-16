/**
 * Synthetic two-account Supabase RLS isolation test.
 * Requires two *existing* synthetic Supabase Auth access tokens on an isolated test project.
 * It performs only SELECT requests and never prints tokens or row-level data.
 *
 * Run locally:
 *   SUPABASE_TEST_URL=... SUPABASE_TEST_PUBLISHABLE_KEY=... \
 *   SUPABASE_TEST_TOKEN_A=... SUPABASE_TEST_TOKEN_B=... \
 *   SUPABASE_TEST_USER_A=... SUPABASE_TEST_USER_B=... \
 *   node tests/supabase_rls_isolation.test.cjs
 *
 * Precondition: provision separate synthetic profiles and progress records through an
 * approved audited backend/test fixture, NOT a browser service key.
 */
"use strict";
const assert=require("node:assert/strict");
const env=process.env;
const required=["SUPABASE_TEST_URL","SUPABASE_TEST_PUBLISHABLE_KEY","SUPABASE_TEST_TOKEN_A","SUPABASE_TEST_TOKEN_B","SUPABASE_TEST_USER_A","SUPABASE_TEST_USER_B"];
if(required.some(k=>!env[k])){console.error("SKIP: isolated synthetic Supabase credentials not configured.");process.exit(0);}
if(!env.SUPABASE_TEST_ALLOW_NONPROD || env.SUPABASE_TEST_ALLOW_NONPROD!=="yes"){
  console.error("SKIP: explicit nonproduction test acknowledgment missing.");process.exit(0);
}
assert.notEqual(env.SUPABASE_TEST_USER_A,env.SUPABASE_TEST_USER_B,"Distinct test users required");
assert.notEqual(env.SUPABASE_TEST_TOKEN_A,env.SUPABASE_TEST_TOKEN_B,"Distinct test tokens required");
const base=new URL(env.SUPABASE_TEST_URL);
assert.equal(base.protocol,"https:");
async function get(path,token){
  const res=await fetch(new URL("/rest/v1/"+path,base),{
    headers:{"apikey":env.SUPABASE_TEST_PUBLISHABLE_KEY,"Authorization":"Bearer "+token,"Accept":"application/json"},
    signal:AbortSignal.timeout(10000)
  });
  assert.equal(res.status,200,"RLS test request did not succeed (HTTP "+res.status+")");
  return res.json();
}
async function main(){
  for(const [own,other,token] of [[env.SUPABASE_TEST_USER_A,env.SUPABASE_TEST_USER_B,env.SUPABASE_TEST_TOKEN_A],
                                    [env.SUPABASE_TEST_USER_B,env.SUPABASE_TEST_USER_A,env.SUPABASE_TEST_TOKEN_B]]){
    for(const table of ["robo_learner_profiles","robo_learning_progress"]){
      const fields=table==="robo_learner_profiles"?"user_id":"user_id,topic_code";
      const ownRows=await get(table+"?select="+fields+"&user_id=eq."+encodeURIComponent(own),token);
      const otherRows=await get(table+"?select="+fields+"&user_id=eq."+encodeURIComponent(other),token);
      assert.ok(Array.isArray(ownRows)&&Array.isArray(otherRows));
      assert.ok(ownRows.length>0,"Missing test fixture for own "+table);
      assert.equal(otherRows.length,0,"Cross-user data exposed in "+table);
    }
  }
  console.log("PASS: two distinct signed-in identities see own fixtures only; cross-user SELECT denied in profiles and progress.");
}
main().catch(e=>{console.error("FAIL: "+e.message);process.exitCode=1;});
