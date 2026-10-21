/* Staging-only opt-in bridge. Never load on production.
   This module needs an already authenticated synthetic Supabase session.
   It does not read existing classroom localStorage identities or send real learner data. */
export async function saveSyntheticClassroomResult({supabaseUrl, publishableKey, accessToken, topicCode, percentage, classLevel, questionCount, correctCount, eventId, completedAt}) {
  if (!/^https:\/\/[a-z0-9]+\.supabase\.co$/.test(supabaseUrl)) throw Error('Invalid staging Supabase endpoint');
  if (typeof accessToken !== 'string' || !accessToken) throw Error('Synthetic sign-in required');
  if (topicCode !== 'synthetic_math_practice') throw Error('Only synthetic topics allowed');
  const score=Number(percentage);
  if (!Number.isInteger(score) || score<0 || score>100) throw Error('Invalid practice score');
  if(!['JSS1','JSS2','JSS3'].includes(classLevel))throw Error('Invalid class level');
  if(!Number.isInteger(questionCount)||questionCount<1||questionCount>200)throw Error('Invalid question count');
  if(!Number.isInteger(correctCount)||correctCount<0||correctCount>questionCount)throw Error('Invalid correct count');
  if(!/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(eventId))throw Error('Invalid event ID');
  const response=await fetch(supabaseUrl+'/rest/v1/robo_synthetic_sync_events',{
    method:'POST',
    headers:{apikey:publishableKey,Authorization:'Bearer '+accessToken,'Content-Type':'application/json',Prefer:'return=minimal'},
    body:JSON.stringify({topic_code:topicCode,score,class_level:classLevel,question_count:questionCount,correct_count:correctCount,practice_event_id:eventId,completed_at:completedAt}),cache:'no-store'
  });
  if(!response.ok){
    const error=Error('Staging-only Supabase sync rejected (HTTP '+response.status+')');
    error.httpStatus=response.status;
    throw error;
  }
  return {saved:true,score};
}
