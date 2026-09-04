const welcome=document.getElementById('welcome');
const classroom=document.getElementById('classroom');
const start=document.getElementById('startLearning');
const toggle=document.getElementById('toggleTeacher');
const teacherPanel=document.getElementById('teacherPanel');
const form=document.getElementById('chatForm');
const question=document.getElementById('question');
const messages=document.getElementById('messages');
const sendButton=form.querySelector('.send');
const uploadButton=document.getElementById('uploadButton');
const cameraButton=document.getElementById('cameraButton');
const imageUpload=document.getElementById('imageUpload');
const cameraCapture=document.getElementById('cameraCapture');
const micButton=document.getElementById('micButton');
const navMicButton=document.getElementById('navMicButton');
const canvasEmpty=document.getElementById('canvasEmpty');
const canvasWork=document.getElementById('canvasWork');
const problemPreview=document.getElementById('problemPreview');
const canvasStatus=document.getElementById('canvasStatus');
const canvasAnswer=document.getElementById('canvasAnswer');
let sessionToken=null;
let previewUrl=null;
let mediaRecorder=null;
let micStream=null;
let recordedChunks=[];

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

function showCanvasAnswer(answer,status='Worked solution'){
  canvasEmpty.classList.add('hidden');canvasWork.classList.remove('hidden');
  canvasStatus.textContent=status;renderLesson(canvasAnswer,answer);
}

function renderLesson(container,text){
  container.replaceChildren();
  text.split(/\n{2,}/).forEach(block=>{
    const paragraph=document.createElement('p');
    block.split('\n').forEach((line,lineIndex)=>{
      if(lineIndex)paragraph.appendChild(document.createElement('br'));
      line.split('**').forEach((part,index)=>{
        const node=index%2?document.createElement('strong'):document.createTextNode(part);
        if(index%2)node.textContent=part;
        paragraph.appendChild(node);
      });
    });
    container.appendChild(paragraph);
  });
}

uploadButton.addEventListener('click',()=>imageUpload.click());
cameraButton.addEventListener('click',()=>cameraCapture.click());
imageUpload.addEventListener('change',()=>handleImage(imageUpload.files[0]));
cameraCapture.addEventListener('change',()=>handleImage(cameraCapture.files[0]));
micButton.addEventListener('click',toggleRecording);
navMicButton.addEventListener('click',toggleRecording);

function setRecordingState(recording){
  micButton.classList.toggle('recording',recording);navMicButton.classList.toggle('recording',recording);
  micButton.textContent=recording?'■':'🎙';navMicButton.textContent=recording?'■ Stop':'🎙 Mic';
  micButton.setAttribute('aria-label',recording?'Stop voice question':'Start voice question');
}

async function toggleRecording(){
  if(mediaRecorder&&mediaRecorder.state==='recording'){mediaRecorder.stop();return;}
  if(!navigator.mediaDevices?.getUserMedia||!window.MediaRecorder){
    addMessage('Voice recording is not supported in this browser. Please type your question instead.','teacher');return;
  }
  try{
    await ensureSession();
    micStream=await navigator.mediaDevices.getUserMedia({audio:true});recordedChunks=[];
    const preferred=['audio/webm;codecs=opus','audio/webm','audio/ogg;codecs=opus'];
    const mimeType=preferred.find(type=>MediaRecorder.isTypeSupported(type));
    mediaRecorder=mimeType?new MediaRecorder(micStream,{mimeType}):new MediaRecorder(micStream);
    mediaRecorder.addEventListener('dataavailable',event=>{if(event.data.size)recordedChunks.push(event.data)});
    mediaRecorder.addEventListener('stop',finishRecording,{once:true});
    mediaRecorder.start();setRecordingState(true);
    addMessage('Listening… Tap Stop when you finish your Maths question.','teacher');
  }catch(_){
    stopMicTracks();setRecordingState(false);
    addMessage('I could not access the microphone. Please allow microphone access or type your question.','teacher');
  }
}

function stopMicTracks(){if(micStream){micStream.getTracks().forEach(track=>track.stop());micStream=null}}

async function finishRecording(){
  setRecordingState(false);stopMicTracks();
  const type=(mediaRecorder?.mimeType||recordedChunks[0]?.type||'audio/webm').split(';',1)[0];
  const blob=new Blob(recordedChunks,{type});mediaRecorder=null;recordedChunks=[];
  if(!blob.size){addMessage('I did not receive any audio. Please try recording again.','teacher');return;}
  if(blob.size>12*1024*1024){addMessage('That recording is too large. Please keep it shorter and try again.','teacher');return;}
  const thinking=addMessage('I’m listening carefully to your Maths question…','teacher');
  micButton.disabled=true;navMicButton.disabled=true;
  try{
    const token=await ensureSession();const body=new FormData();body.append('session_token',token);
    body.append('audio',blob,`maths-question.${type.includes('ogg')?'ogg':'webm'}`);
    const response=await fetch('/api/classroom/audio',{method:'POST',headers:{'Accept':'application/json'},body});
    const data=await response.json();
    if(response.status===401){sessionToken=null;throw new Error('session');}
    if(!response.ok)throw new Error(data.detail||'request');
    canvasWork.classList.add('text-only');problemPreview.hidden=true;
    showCanvasAnswer(data.reply,'Voice question explained');
    thinking.textContent='I’ve placed the complete answer to your voice question on the Teaching Canvas.';
  }catch(err){
    const detail=err.message||'';
    thinking.textContent=detail&&!['request','session','Failed to fetch'].includes(detail)?detail:'I could not process that recording. Please try again or type your question.';
  }finally{micButton.disabled=false;navMicButton.disabled=false;}
}

async function handleImage(file){
  if(!file)return;
  if(!['image/jpeg','image/png','image/webp'].includes(file.type)){
    addMessage('Please choose a JPEG, PNG, or WebP image.','teacher');return;
  }
  if(file.size>8*1024*1024){addMessage('Please choose an image no larger than 8 MB.','teacher');return;}
  if(previewUrl)URL.revokeObjectURL(previewUrl);
  previewUrl=URL.createObjectURL(file);problemPreview.src=previewUrl;
  canvasWork.classList.remove('text-only');problemPreview.hidden=false;
  canvasEmpty.classList.add('hidden');canvasWork.classList.remove('hidden');
  canvasStatus.textContent='Robo-Teacher is reading your image…';canvasAnswer.textContent='';
  const thinking=addMessage('I’m reading the Maths problem in your image…','teacher');
  uploadButton.disabled=true;cameraButton.disabled=true;
  try{
    const token=await ensureSession();
    const body=new FormData();body.append('session_token',token);body.append('image',file);
    const caption=question.value.trim();if(caption)body.append('caption',caption);
    const response=await fetch('/api/classroom/image',{method:'POST',headers:{'Accept':'application/json'},body});
    const data=await response.json();
    if(response.status===401){sessionToken=null;throw new Error('session');}
    if(!response.ok)throw new Error(data.detail||'request');
    showCanvasAnswer(data.reply,'Teaching response ready');
    thinking.textContent='I’ve placed the complete image explanation on the Teaching Canvas.';
    question.value='';
  }catch(err){
    const message=err.message&&err.message!=='request'&&err.message!=='session'?err.message:'I could not read that image. Please try a clearer photo.';
    thinking.textContent=message;canvasStatus.textContent='Image needs attention';
  }finally{uploadButton.disabled=false;cameraButton.disabled=false;imageUpload.value='';cameraCapture.value='';}
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
    canvasWork.classList.add('text-only');problemPreview.hidden=true;
    showCanvasAnswer(data.reply,'Worked solution');
    thinking.textContent='I’ve placed the complete worked solution on the Teaching Canvas.';
  }catch(err){
    thinking.textContent=err.message&&err.message.includes('wait')?err.message:'Sorry, I had a small technical hiccup. Please try your question again in a moment.';
  }finally{sendButton.disabled=false;sendButton.textContent='Send';question.focus()}
});
