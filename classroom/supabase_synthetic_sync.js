/* Staging-only opt-in bridge. Never load on production.
   This module needs an already authenticated synthetic Supabase session.
   It does not read existing classroom localStorage identities or send real learner data. */
export async function saveSyntheticClassroomResult({supabaseUrl, publishableKey, accessToken, topicCode, percentage}) {
  if (!/^https:\/\/[a-z0-9]+\.supabase\.co$/.test(supabaseUrl)) throw Error('Invalid staging Supabase endpoint');
  if (typeof accessToken !== 'string' || !accessToken) throw Error('Synthetic sign-in required');
  if (topicCode !== 'synthetic_math_practice') throw Error('Only synthetic topics allowed');
  const score=Number(percentage);
  if (!Number.isInteger(score) || score<0 || score>100) throw Error('Invalid practice score');
  const response=await fetch(supabaseUrl+'/rest/v1/robo_synthetic_sync_events',{
    method:'POST',
    headers:{apikey:publishableKey,Authorization:'Bearer '+accessToken,'Content-Type':'application/json',Prefer:'return=minimal'},
    body:JSON.stringify({topic_code:topicCode,score}),cache:'no-store'
  });
  if(!response.ok)throw Error('Staging-only Supabase sync rejected (HTTP '+response.status+')');
  return {saved:true,score};
}
