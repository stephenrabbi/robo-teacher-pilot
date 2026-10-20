import {saveSyntheticClassroomResult} from '/classroom/supabase_synthetic_sync.js';
const panel=document.getElementById('syntheticCloudSync');
const status=document.getElementById('syntheticCloudStatus');
const authURL='https://drzaxpofuhqchmpkwhpy.supabase.co';
const publishableKey='sb_publishable_FXqz6Ky3ypQxNXPlJiT1XA_X5onZmE7';
let session=null, expiry=0;
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
const clearResults=()=>{cloudResults.replaceChildren();refresh.hidden=true};
async function retrieveScores(){
 if(!enabled||!session){clearResults();return}
 if(expiry&&Date.now()>=expiry*1000){clearSession();setStatus('Session expired. Sign in again.');return}
 const activeSession=session;
 try{
  const url=authURL+'/rest/v1/robo_synthetic_sync_events?select=topic_code,score,created_at&order=created_at.desc&limit=20';
  const response=await fetch(url,{headers:{apikey:publishableKey,Authorization:'Bearer '+activeSession.token,Accept:'application/json'},cache:'no-store'});
  if(!response.ok)throw Error('Cloud retrieval rejected (HTTP '+response.status+').');
  const rows=await response.json();
  if(activeSession!==session)return;
  if(!Array.isArray(rows))throw Error('Unexpected cloud response.');
  const list=document.createElement('ul');
  for(const row of rows){
   if(row.topic_code!=='synthetic_math_practice'||!Number.isInteger(row.score)||row.score<0||row.score>100)continue;
   const item=document.createElement('li');
   const date=new Date(row.created_at);
   item.textContent='Mathematics practice: '+row.score+'% — '+(Number.isNaN(date.getTime())?'date unavailable':date.toLocaleString());
   list.append(item);
  }
  cloudResults.replaceChildren(list);
  if(!list.children.length)cloudResults.textContent='No synthetic mathematics scores found for this account.';
 }catch(e){if(activeSession===session)cloudResults.textContent='Unable to retrieve saved scores: '+e.message}
}
refresh.addEventListener('click',()=>{void retrieveScores()});
function clearSession(){session=null;expiry=0;document.getElementById('syntheticCloudPassword').value='';clearResults();setStatus('Synthetic session cleared.');}
const enabled=new URLSearchParams(location.search).get('synthetic_cloud')==='1';
if(enabled)panel.hidden=false;
document.getElementById('syntheticCloudLogout').addEventListener('click',clearSession);
document.getElementById('syntheticCloudLogin').addEventListener('click',async()=>{
 if(!enabled)return;
 const email=document.getElementById('syntheticCloudEmail').value.trim().toLowerCase();
 const password=document.getElementById('syntheticCloudPassword').value;
 document.getElementById('syntheticCloudPassword').value='';
 if(!/^robotest\.learner\.[ab]@example\.com$/.test(email)){setStatus('Synthetic A/B accounts only.');return}
 try{
  const r=await fetch(authURL+'/auth/v1/token?grant_type=password',{method:'POST',headers:{apikey:publishableKey,'Content-Type':'application/json'},body:JSON.stringify({email,password}),cache:'no-store'});
  if(!r.ok)throw Error('Synthetic sign-in rejected (HTTP '+r.status+').');
  const data=await r.json();
  if(data.user?.email?.toLowerCase()!==email||!data.access_token)throw Error('Synthetic account mismatch');
  session={token:data.access_token,userId:data.user.id};expiry=Number(data.expires_at||0);
  setStatus('Synthetic cloud session ready. Complete a mathematics practice to test progress saving.');
  refresh.hidden=false;
  await retrieveScores();
 }catch(e){clearSession();setStatus(e.message)}
});
async function saveSummary(summary){
 if(!enabled||!session)return;
 if(expiry&&Date.now()>=expiry*1000){clearSession();setStatus('Session expired. Sign in again.');return}
 const score=Number(summary?.percentage);
 if(!Number.isInteger(score)||score<0||score>100){setStatus('Practice percentage unavailable for cloud sync.');return}
 try {
  await saveSyntheticClassroomResult({supabaseUrl:authURL,publishableKey,accessToken:session.token,topicCode:'synthetic_math_practice',percentage:score});
  setStatus('Synthetic practice score '+score+' saved to Supabase. No production learner records changed.');
  await retrieveScores();
 }catch(e){setStatus('Cloud sync skipped: '+e.message)}
}
document.addEventListener('robo:practice-completed',e=>{void saveSummary(e.detail)});
