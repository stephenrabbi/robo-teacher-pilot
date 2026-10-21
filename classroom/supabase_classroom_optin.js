import {saveSyntheticClassroomResult} from '/classroom/supabase_synthetic_sync.js';
const panel=document.getElementById('syntheticCloudSync');
const status=document.getElementById('syntheticCloudStatus');
const authURL='https://drzaxpofuhqchmpkwhpy.supabase.co';
const publishableKey='sb_publishable_FXqz6Ky3ypQxNXPlJiT1XA_X5onZmE7';
let session=null, expiry=0, savePending=false, loginAttempt=0;
const savedEventIds=new Set();
// Keep synthetic tokens in memory only; never mix them with classroom learner identity.
const setStatus=x=>{status.textContent=x};
const cloudResults=document.createElement('div');
cloudResults.id='syntheticCloudResults';
cloudResults.setAttribute('aria-live','polite');
const refresh=document.createElement('button');
refresh.id='syntheticCloudRefresh';
refresh.type='button';
refresh.textContent='Retrieve saved synthetic scores';
refresh.hidden=true;
panel.append(refresh,cloudResults);
// Staging-only authenticated cloud history within the regular Progress screen.
// Never replace its existing local metrics or its learner identity.
const progressArea=document.getElementById('progressArea');
const cloudSection=document.createElement('section');
cloudSection.id='syntheticProgressCloudHistory';
cloudSection.setAttribute('aria-label','Synthetic authenticated cloud practice history');
cloudSection.style.cssText='margin:1rem 0;padding:1rem;border:1px solid #aab6c5;border-radius:10px;';
const cloudTitle=document.createElement('h4');
cloudTitle.textContent='Cloud practice history (synthetic test only)';
const cloudNote=document.createElement('p');
cloudNote.textContent='Authenticated synthetic account scores only. These do not change the local dashboard totals or learning recommendations.';
const cloudRestoreStatus=document.createElement('p');
cloudRestoreStatus.id='syntheticCloudRestoreStatus';
cloudRestoreStatus.setAttribute('role','status');
cloudRestoreStatus.textContent='Sign in to restore a read-only cloud practice snapshot from this synthetic account.';
const cloudMetrics=document.createElement('div');
cloudMetrics.id='syntheticCloudMetrics';
cloudMetrics.setAttribute('aria-live','polite');
const topicPerformance=document.createElement('div');
topicPerformance.id='syntheticTopicPerformance';
const cloudProgressResults=document.createElement('div');
cloudProgressResults.setAttribute('aria-live','polite');
const cloudProgressRefresh=document.createElement('button');
cloudProgressRefresh.type='button';
cloudProgressRefresh.textContent='Refresh cloud practice history';
cloudProgressRefresh.addEventListener('click',()=>{void retrieveScores(true)});
cloudSection.append(cloudTitle,cloudNote,cloudProgressRefresh,cloudRestoreStatus,cloudMetrics,topicPerformance,cloudProgressResults);


const clearResults=()=>{cloudRestoreStatus.textContent='Sign in to restore a read-only cloud practice snapshot from this synthetic account.';cloudResults.replaceChildren();cloudProgressResults.replaceChildren();cloudMetrics.replaceChildren();topicPerformance.replaceChildren();cloudProgressResults.textContent='Sign in to a synthetic account in the cloud test panel below to see authenticated scores.';refresh.hidden=true};
async function retrieveScores(manual=false){
 if(!enabled)return;
 if(!session){clearResults();if(manual){cloudProgressResults.textContent='Cloud session not connected. Sign in using the Synthetic cloud progress test panel below, then refresh again.';setStatus('Sign in to a synthetic account before refreshing cloud history.')}return}
 if(expiry&&Date.now()>=expiry*1000){clearSession();setStatus('Session expired. Sign in again.');return}
 const activeSession=session;
 cloudRestoreStatus.textContent='Loading authenticated cloud practice snapshot…';
 if(manual){cloudProgressRefresh.disabled=true;cloudProgressRefresh.textContent='Refreshing cloud history…';cloudProgressResults.textContent='Checking authenticated cloud practice history…'}
 try{
  const url=authURL+'/rest/v1/robo_synthetic_sync_events?select=topic_code,score,created_at,class_level,question_count,correct_count,practice_event_id,topic_label&order=created_at.desc&limit=20';
  const response=await fetch(url,{headers:{apikey:publishableKey,Authorization:'Bearer '+activeSession.token,Accept:'application/json'},cache:'no-store'});
  if(!response.ok)throw Error('Cloud retrieval rejected (HTTP '+response.status+').');
  const rows=await response.json();
  if(activeSession!==session)return;
  if(!Array.isArray(rows))throw Error('Unexpected cloud response.');
  const list=document.createElement('ul');
  const scores=[];
  let enrichedCount=0,questions=0,correct=0;
  const topics=new Map();
  for(const row of rows){
   if(row.topic_code!=='synthetic_math_practice'||!Number.isInteger(row.score)||row.score<0||row.score>100)continue;
   scores.push(row.score);
   if(row.practice_event_id&&Number.isInteger(row.question_count)&&row.question_count>0&&Number.isInteger(row.correct_count)&&row.correct_count>=0&&row.correct_count<=row.question_count){enrichedCount++;questions+=row.question_count;correct+=row.correct_count;}
   if(row.practice_event_id&&typeof row.topic_label==='string'&&row.topic_label.trim()&&['JSS1','JSS2','JSS3'].includes(row.class_level)&&Number.isInteger(row.question_count)&&row.question_count>0&&Number.isInteger(row.correct_count)&&row.correct_count>=0&&row.correct_count<=row.question_count){
    const key=row.class_level+' · '+row.topic_label.trim();
    const aggregate=topics.get(key)||{sessions:0,attempted:0,correct:0};
    aggregate.sessions++;aggregate.attempted+=row.question_count;aggregate.correct+=row.correct_count;
    topics.set(key,aggregate);
   }
   const item=document.createElement('li');
   const date=new Date(row.created_at);
   item.textContent='Mathematics practice'+(row.topic_label?' — '+row.topic_label:'')+(row.class_level?' ('+row.class_level+')':'')+': '+row.score+'%'+(Number.isInteger(row.question_count)&&Number.isInteger(row.correct_count)?' · '+row.correct_count+'/'+row.question_count+' questions':'')+' — '+(Number.isNaN(date.getTime())?'date unavailable':date.toLocaleString());
   list.append(item);
  }
  cloudMetrics.replaceChildren();
  if(scores.length){
   const sum=scores.reduce((total,score)=>total+score,0);
   const latest=document.createElement('p');
   const avg=Math.round(sum/scores.length);
   latest.textContent='Cloud summary (last '+scores.length+' saved records): latest '+scores[0]+'% · average '+avg+'% · '+scores.length+' recorded practices.';
   const caveat=document.createElement('p');
   caveat.textContent=enrichedCount?'Verified event metadata in '+enrichedCount+' of '+scores.length+' retrieved records: '+correct+'/'+questions+' questions correct. Older percentage-only records are excluded from these question totals. Topic mastery and personalised recommendations remain unavailable.':'These are synthetic score-only records, not verified unique practice sessions. Topic mastery, question counts and personalised recommendations cannot be calculated from them.';
   cloudMetrics.append(latest,caveat);
  }
  cloudRestoreStatus.textContent='Cloud practice snapshot restored (read-only): '+scores.length+' saved records, '+enrichedCount+' enriched practice events, '+topics.size+' recorded topics. Local progress and recommendations were not changed.';
  topicPerformance.replaceChildren();
  if(topics.size){
   const heading=document.createElement('h5');heading.textContent='Recorded topic performance (synthetic only)';
   const detail=document.createElement('p');detail.textContent='Cloud-derived learning evidence from enriched records for this authenticated account (maximum 20). Results are descriptive only: no mastery rating, adaptive placement, or recommendation is inferred.';
   const topicList=document.createElement('ul');topicList.style.cssText='list-style:none;padding:0;margin:0;max-width:100%;';
   for(const [topic,metric] of topics){
    const item=document.createElement('li');
    item.style.cssText='margin:.7rem 0;padding:.8rem;border:1px solid #b8c2ce;border-radius:8px;overflow-wrap:anywhere;max-width:100%;box-sizing:border-box;';
    const topicName=document.createElement('strong');topicName.textContent=topic;
    const observed=Math.round(100*metric.correct/metric.attempted);
    const scoreLine=document.createElement('p');scoreLine.textContent=metric.correct+'/'+metric.attempted+' correct ('+observed+'%) across '+metric.sessions+' recorded practice'+(metric.sessions===1?'':'s')+'.';
    const evidence=document.createElement('p');evidence.textContent='Evidence: '+(metric.sessions<3||metric.attempted<15?'limited — more practice needed before assessing a learning trend':'multiple practices recorded — review performance across sessions before drawing conclusions')+'.';
    const meter=document.createElement('progress');meter.value=metric.correct;meter.max=metric.attempted;meter.setAttribute('aria-label',topic+' observed correct answers');meter.style.cssText='display:block;width:100%;max-width:100%;margin:.6rem 0;';
    item.append(topicName,scoreLine,meter,evidence);
    topicList.append(item);
   }
   topicPerformance.append(heading,detail,topicList);
  }
  cloudResults.replaceChildren(list);
  cloudProgressResults.replaceChildren(list.cloneNode(true));
  if(!list.children.length){cloudResults.textContent='No synthetic mathematics scores found for this account.';cloudProgressResults.textContent=cloudResults.textContent;}
  if(manual)setStatus('Cloud history refreshed: '+scores.length+' mathematics records retrieved.');
 }catch(e){
  if(activeSession!==session)return;
  cloudRestoreStatus.textContent='Cloud practice snapshot unavailable: '+e.message;
  cloudResults.textContent='Unable to retrieve saved scores: '+e.message;
  cloudProgressResults.textContent=cloudResults.textContent;
  cloudMetrics.replaceChildren();topicPerformance.replaceChildren();
  if(/401|403/.test(e.message)){clearSession();setStatus('Cloud session expired or access denied. Sign in again.')}
  else if(manual)setStatus('Cloud history refresh failed: '+e.message);
 }finally{if(manual){cloudProgressRefresh.disabled=false;cloudProgressRefresh.textContent='Refresh cloud practice history'}}
}
refresh.addEventListener('click',()=>{void retrieveScores()});
function clearSession(){loginAttempt++;savedEventIds.clear();session=null;expiry=0;document.getElementById('syntheticCloudPassword').value='';clearResults();setStatus('Synthetic session cleared.');}
const enabled=new URLSearchParams(location.search).get('synthetic_cloud')==='1';
if(enabled){panel.hidden=false;progressArea.append(cloudSection);clearResults();}
// Refresh only on opening the existing Progress screen, not continuously.
if(enabled){const observer=new MutationObserver(()=>{if(!progressArea.classList.contains('hidden')&&session)void retrieveScores()});observer.observe(progressArea,{attributes:true,attributeFilter:['class']});}
document.getElementById('syntheticCloudLogout').addEventListener('click',clearSession);
document.getElementById('syntheticCloudLogin').addEventListener('click',async()=>{
 if(!enabled)return;
 const attempt=++loginAttempt;
 const email=document.getElementById('syntheticCloudEmail').value.trim().toLowerCase();
 const password=document.getElementById('syntheticCloudPassword').value;
 document.getElementById('syntheticCloudPassword').value='';
 if(!/^robotest\.learner\.[ab]@example\.com$/.test(email)){setStatus('Synthetic A/B accounts only.');return}
 try{
  const r=await fetch(authURL+'/auth/v1/token?grant_type=password',{method:'POST',headers:{apikey:publishableKey,'Content-Type':'application/json'},body:JSON.stringify({email,password}),cache:'no-store'});
  if(!r.ok)throw Error('Synthetic sign-in rejected (HTTP '+r.status+').');
  const data=await r.json();
  if(attempt!==loginAttempt)return;
  if(data.user?.email?.toLowerCase()!==email||!data.access_token)throw Error('Synthetic account mismatch');
  session={token:data.access_token,userId:data.user.id};expiry=Number(data.expires_at||0);
  setStatus('Synthetic cloud session ready. Complete a mathematics practice to test progress saving.');
  refresh.hidden=false;
  await retrieveScores();
 }catch(e){if(attempt===loginAttempt){clearSession();setStatus(e.message)}}
});
async function saveSummary(summary){
 if(!enabled||!session||savePending)return;
 if(expiry&&Date.now()>=expiry*1000){clearSession();setStatus('Session expired. Sign in again.');return}
 const score=Number(summary?.percentage);
 if(!Number.isInteger(score)||score<0||score>100){setStatus('Practice percentage unavailable for cloud sync.');return}
 if(typeof summary?.eventId!=='string')return;
 if(savedEventIds.has(summary.eventId)){setStatus('This synthetic practice result was already saved. No duplicate was created.');return}
 const activeSession=session;
 savePending=true;
 try {
  await saveSyntheticClassroomResult({supabaseUrl:authURL,publishableKey,accessToken:session.token,topicCode:'synthetic_math_practice',percentage:score,classLevel:summary.classLevel,questionCount:summary.questionCount,correctCount:summary.correctCount,eventId:summary.eventId,completedAt:summary.completedAt,topicLabel:summary.topicLabel});
  if(activeSession!==session)return;
  savedEventIds.add(summary.eventId);
  setStatus('Synthetic practice score '+score+' saved to Supabase. No production learner records changed.');
  await retrieveScores();
 }catch(e){
  if(activeSession===session){
   if(e.httpStatus===401||e.httpStatus===403){clearSession();setStatus('Cloud save authorization expired or was denied. Sign in again before saving new practice results.');}
   else setStatus('Cloud sync skipped: '+e.message);
  }
 }
 finally{savePending=false}
}
document.addEventListener('robo:practice-completed',e=>{void saveSummary(e.detail)});
