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
const canvasEmpty=document.getElementById('canvasEmpty');
const canvasWork=document.getElementById('canvasWork');
const problemPreview=document.getElementById('problemPreview');
const canvasStatus=document.getElementById('canvasStatus');
const canvasAnswer=document.getElementById('canvasAnswer');
let sessionToken=null;
let previewUrl=null;

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
