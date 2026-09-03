const welcome=document.getElementById('welcome');
const classroom=document.getElementById('classroom');
const start=document.getElementById('startLearning');
const toggle=document.getElementById('toggleTeacher');
const teacherPanel=document.getElementById('teacherPanel');
const form=document.getElementById('chatForm');
const question=document.getElementById('question');
const messages=document.getElementById('messages');
const sendButton=form.querySelector('.send');
let sessionToken=null;

async function ensureSession(){
  if(sessionToken)return sessionToken;
  const response=await fetch('/api/classroom/session',{method:'POST',headers:{'Accept':'application/json'}});
  if(!response.ok)throw new Error('session');
  const data=await response.json();
  sessionToken=data.session_token;
  return sessionToken;
}

start.addEventListener('click',async()=>{
  welcome.classList.add('hidden');classroom.classList.remove('hidden');question.focus();
  try{await ensureSession()}catch(_){addMessage('I could not start the classroom connection. Please refresh and try again.','teacher')}
});

toggle.addEventListener('click',()=>{
  const mini=teacherPanel.classList.toggle('minimized');
  classroom.classList.toggle('teacher-min',mini);
  toggle.textContent=mini?'↗':'↙';
  toggle.setAttribute('aria-label',mini?'Maximize teacher':'Minimize teacher');
});

function addMessage(text,role){
  const el=document.createElement('div');el.className=`message ${role}`;el.textContent=text;
  messages.appendChild(el);messages.scrollTop=messages.scrollHeight;return el;
}

form.addEventListener('submit',async(e)=>{
  e.preventDefault();const text=question.value.trim();if(!text||sendButton.disabled)return;
  addMessage(text,'student');question.value='';sendButton.disabled=true;sendButton.textContent='Thinking…';
  const thinking=addMessage('Let me work through that with you…','teacher');
  try{
    const token=await ensureSession();
    const response=await fetch('/api/classroom/chat',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({message:text,session_token:token})});
    const data=await response.json();
    if(response.status===401){sessionToken=null;throw new Error('session');}
    if(!response.ok)throw new Error(data.detail||'request');
    thinking.textContent=data.reply;
  }catch(err){
    thinking.textContent=err.message&&err.message.includes('wait')?err.message:'Sorry, I had a small technical hiccup. Please try your question again in a moment.';
  }finally{sendButton.disabled=false;sendButton.textContent='Send';question.focus()}
});
