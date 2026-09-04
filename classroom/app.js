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
const whiteboardButton=document.getElementById('whiteboardButton');
const whiteboardArea=document.getElementById('whiteboardArea');
const whiteboard=document.getElementById('whiteboard');
const penTool=document.getElementById('penTool');
const eraserTool=document.getElementById('eraserTool');
const clearBoardButton=document.getElementById('clearBoard');
const closeBoardButton=document.getElementById('closeBoard');
const submitBoardButton=document.getElementById('submitBoard');
const backToWhiteboard=document.getElementById('backToWhiteboard');
const language=document.getElementById('language');
const languageButton=document.getElementById('languageButton');
const practiceButton=document.getElementById('practiceButton');
const practiceArea=document.getElementById('practiceArea');
const practiceSetup=document.getElementById('practiceSetup');
const practiceQuestion=document.getElementById('practiceQuestion');
const practiceTopic=document.getElementById('practiceTopic');
const practiceDifficulty=document.getElementById('practiceDifficulty');
const startPracticeButton=document.getElementById('startPractice');
const practiceProgress=document.getElementById('practiceProgress');
const practiceScore=document.getElementById('practiceScore');
const practiceContext=document.getElementById('practiceContext');
const practicePrompt=document.getElementById('practicePrompt');
const practiceForm=document.getElementById('practiceForm');
const practiceAnswer=document.getElementById('practiceAnswer');
const showHintButton=document.getElementById('showHint');
const nextPracticeButton=document.getElementById('nextPractice');
const closePracticeButton=document.getElementById('closePractice');
const practiceFeedback=document.getElementById('practiceFeedback');
let currentPractice=null;
let sessionToken=null;
let previewUrl=null;
let mediaRecorder=null;
let micStream=null;
let recordedChunks=[];
let drawing=false;
let drawingTool='pen';
let boardHasInk=false;
const boardContext=whiteboard.getContext('2d');
const savedLanguage=localStorage.getItem('roboTeacherLanguage');
if(['English','Yoruba','Igbo','Hausa'].includes(savedLanguage))language.value=savedLanguage;

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
  whiteboardArea.classList.add('hidden');practiceArea.classList.add('hidden');canvasEmpty.classList.add('hidden');canvasWork.classList.remove('hidden');
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
whiteboardButton.addEventListener('click',openWhiteboard);
closeBoardButton.addEventListener('click',closeWhiteboard);
penTool.addEventListener('click',()=>selectDrawingTool('pen'));
eraserTool.addEventListener('click',()=>selectDrawingTool('eraser'));
clearBoardButton.addEventListener('click',clearWhiteboard);
submitBoardButton.addEventListener('click',submitWhiteboard);
whiteboard.addEventListener('pointerdown',startDrawing);
whiteboard.addEventListener('pointermove',drawOnWhiteboard);
whiteboard.addEventListener('pointerup',stopDrawing);
whiteboard.addEventListener('pointercancel',stopDrawing);
backToWhiteboard.addEventListener('click',openWhiteboard);
language.addEventListener('change',()=>{
  localStorage.setItem('roboTeacherLanguage',language.value);
  const notices={English:'I will teach you in English from now on.',Yoruba:'Mo máa kọ́ ọ ní Yorùbá láti ìsinsin yìí.',Igbo:'Aga m akụziri gị ihe n’Igbo site ugbu a.',Hausa:'Zan koyar da kai da Hausa daga yanzu.'};
  addMessage(notices[language.value],'teacher');
  question.focus();
});
languageButton.addEventListener('click',()=>language.focus());
practiceButton.addEventListener('click',openPractice);
startPracticeButton.addEventListener('click',startPracticeSession);
practiceForm.addEventListener('submit',submitPracticeAnswer);
showHintButton.addEventListener('click',showPracticeHint);
nextPracticeButton.addEventListener('click',loadNextPracticeQuestion);
closePracticeButton.addEventListener('click',closePractice);

function openPractice(){
  whiteboardArea.classList.add('hidden');canvasWork.classList.add('hidden');canvasEmpty.classList.add('hidden');practiceArea.classList.remove('hidden');
  if(currentPractice){practiceSetup.classList.add('hidden');practiceQuestion.classList.remove('hidden');practiceAnswer.focus()}
  else{practiceSetup.classList.remove('hidden');practiceQuestion.classList.add('hidden')}
}

function closePractice(){
  practiceArea.classList.add('hidden');
  if(canvasAnswer.textContent.trim())canvasWork.classList.remove('hidden');else canvasEmpty.classList.remove('hidden');
}

function renderPracticeQuestion(data){
  currentPractice=data;practiceSetup.classList.add('hidden');practiceQuestion.classList.remove('hidden');
  practiceProgress.textContent=`Question ${data.question_number}`;practiceScore.textContent=`Score: ${data.score}/${data.attempted}`;
  practiceContext.textContent=`${data.topic} · ${data.difficulty}`;practicePrompt.textContent=data.question;
  practiceAnswer.value='';practiceAnswer.disabled=false;practiceForm.querySelector('button').disabled=false;
  practiceFeedback.textContent='';practiceFeedback.className='practice-feedback hidden';showHintButton.disabled=false;
  showHintButton.textContent='Show Hint';nextPracticeButton.classList.add('hidden');practiceAnswer.focus();
}

async function practiceRequest(path,body){
  const token=await ensureSession();
  const response=await fetch(`/api/classroom/practice/${path}`,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({session_token:token,...body})});
  const data=await response.json();if(response.status===401)sessionToken=null;if(!response.ok)throw new Error(data.detail||'Practice request failed');return data;
}

async function startPracticeSession(){
  startPracticeButton.disabled=true;startPracticeButton.textContent='Preparing…';
  try{renderPracticeQuestion(await practiceRequest('start',{topic:practiceTopic.value,difficulty:practiceDifficulty.value}))}
  catch(err){addMessage(err.message,'teacher')}
  finally{startPracticeButton.disabled=false;startPracticeButton.textContent='Start Practice →'}
}

function showPracticeHint(){
  if(!currentPractice)return;practiceFeedback.textContent=`Hint: ${currentPractice.hint}`;practiceFeedback.className='practice-feedback';showHintButton.disabled=true;showHintButton.textContent='Hint shown';
}

async function submitPracticeAnswer(event){
  event.preventDefault();const answer=practiceAnswer.value.trim();if(!answer)return;
  const checkButton=practiceForm.querySelector('button');checkButton.disabled=true;
  try{
    const result=await practiceRequest('answer',{answer});practiceAnswer.disabled=true;
    practiceScore.textContent=`Score: ${result.score}/${result.attempted} (${result.percentage}%)`;
    practiceFeedback.textContent=result.correct?`Correct! ${result.explanation}`:`Not quite. The correct answer is ${result.expected_answer}. ${result.explanation}`;
    practiceFeedback.className=`practice-feedback ${result.correct?'correct':'incorrect'}`;nextPracticeButton.classList.remove('hidden');showHintButton.disabled=true;
  }catch(err){practiceFeedback.textContent=err.message;practiceFeedback.className='practice-feedback incorrect';checkButton.disabled=false}
}

async function loadNextPracticeQuestion(){
  nextPracticeButton.disabled=true;
  try{renderPracticeQuestion(await practiceRequest('next',{}))}
  catch(err){practiceFeedback.textContent=err.message;practiceFeedback.className='practice-feedback incorrect'}
  finally{nextPracticeButton.disabled=false}
}

function clearWhiteboard(){
  boardContext.save();boardContext.fillStyle='#ffffff';boardContext.fillRect(0,0,whiteboard.width,whiteboard.height);boardContext.restore();
  boardHasInk=false;
}

function openWhiteboard(){
  canvasEmpty.classList.add('hidden');canvasWork.classList.add('hidden');practiceArea.classList.add('hidden');whiteboardArea.classList.remove('hidden');
  if(!whiteboard.dataset.ready){clearWhiteboard();whiteboard.dataset.ready='true'}
}

function closeWhiteboard(){
  whiteboardArea.classList.add('hidden');
  if(canvasAnswer.textContent.trim())canvasWork.classList.remove('hidden');else canvasEmpty.classList.remove('hidden');
}

function selectDrawingTool(tool){
  drawingTool=tool;penTool.classList.toggle('active',tool==='pen');eraserTool.classList.toggle('active',tool==='eraser');
}

function boardPoint(event){
  const rect=whiteboard.getBoundingClientRect();
  return {x:(event.clientX-rect.left)*whiteboard.width/rect.width,y:(event.clientY-rect.top)*whiteboard.height/rect.height};
}

function startDrawing(event){
  drawing=true;whiteboard.setPointerCapture(event.pointerId);const point=boardPoint(event);
  boardContext.beginPath();boardContext.moveTo(point.x,point.y);event.preventDefault();
}

function drawOnWhiteboard(event){
  if(!drawing)return;const point=boardPoint(event);
  boardContext.lineCap='round';boardContext.lineJoin='round';
  boardContext.strokeStyle=drawingTool==='eraser'?'#ffffff':'#10203a';
  boardContext.lineWidth=drawingTool==='eraser'?34:6;
  boardContext.lineTo(point.x,point.y);boardContext.stroke();event.preventDefault();
  if(drawingTool==='pen')boardHasInk=true;
}

function stopDrawing(event){
  if(!drawing)return;drawOnWhiteboard(event);drawing=false;boardContext.closePath();
}

async function submitWhiteboard(){
  if(!boardHasInk){addMessage('Please write a Maths problem or show some working on the whiteboard first.','teacher');return;}
  submitBoardButton.disabled=true;submitBoardButton.textContent='Preparing…';
  const imageData=whiteboard.toDataURL('image/png');
  problemPreview.src=imageData;canvasWork.classList.remove('text-only');problemPreview.hidden=false;
  backToWhiteboard.classList.remove('hidden');whiteboardArea.classList.add('hidden');
  canvasEmpty.classList.add('hidden');canvasWork.classList.remove('hidden');
  canvasStatus.textContent='Robo-Teacher is reading your whiteboard…';canvasAnswer.textContent='';
  const thinking=addMessage('I’m reading the Maths work on your whiteboard…','teacher');
  try{
    const token=await ensureSession();
    const response=await fetch('/api/classroom/whiteboard',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({session_token:token,image_data:imageData,caption:question.value.trim(),language:language.value})});
    const data=await response.json();
    if(response.status===401){sessionToken=null;throw new Error('session');}
    if(!response.ok)throw new Error(data.detail||'request');
    showCanvasAnswer(data.reply,'Whiteboard solution ready');
    thinking.textContent='I’ve placed the complete whiteboard explanation on the Teaching Canvas.';question.value='';
  }catch(err){
    const detail=err.message||'';
    thinking.textContent=detail&&!['request','session','Failed to fetch'].includes(detail)?detail:'I could not send that whiteboard. Please return to it and try again.';
    canvasStatus.textContent='Whiteboard needs attention';
  }finally{submitBoardButton.disabled=false;submitBoardButton.textContent='Ask Teacher →';}
}

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
    const token=await ensureSession();const body=new FormData();body.append('session_token',token);body.append('language',language.value);
    body.append('audio',blob,`maths-question.${type.includes('ogg')?'ogg':'webm'}`);
    const response=await fetch('/api/classroom/audio',{method:'POST',headers:{'Accept':'application/json'},body});
    const data=await response.json();
    if(response.status===401){sessionToken=null;throw new Error('session');}
    if(!response.ok)throw new Error(data.detail||'request');
    canvasWork.classList.add('text-only');problemPreview.hidden=true;
    backToWhiteboard.classList.add('hidden');
    showCanvasAnswer(data.reply,'Voice question explained');
    thinking.textContent='I’ve placed the complete answer to your voice question on the Teaching Canvas.';
  }catch(err){
    const detail=err.message||'';
    thinking.textContent=detail&&!['request','session','Failed to fetch'].includes(detail)?detail:'I could not process that recording. Please try again or type your question.';
  }finally{micButton.disabled=false;navMicButton.disabled=false;}
}

async function handleImage(file,source='upload'){
  if(!file)return;
  if(!['image/jpeg','image/png','image/webp'].includes(file.type)){
    addMessage('Please choose a JPEG, PNG, or WebP image.','teacher');return;
  }
  if(file.size>8*1024*1024){addMessage('Please choose an image no larger than 8 MB.','teacher');return;}
  if(previewUrl)URL.revokeObjectURL(previewUrl);
  previewUrl=URL.createObjectURL(file);problemPreview.src=previewUrl;
  canvasWork.classList.remove('text-only');problemPreview.hidden=false;
  backToWhiteboard.classList.toggle('hidden',source!=='whiteboard');
  whiteboardArea.classList.add('hidden');
  canvasEmpty.classList.add('hidden');canvasWork.classList.remove('hidden');
  canvasStatus.textContent='Robo-Teacher is reading your image…';canvasAnswer.textContent='';
  const thinking=addMessage('I’m reading the Maths problem in your image…','teacher');
  uploadButton.disabled=true;cameraButton.disabled=true;
  try{
    const token=await ensureSession();
    const body=new FormData();body.append('session_token',token);body.append('language',language.value);body.append('image',file);
    const caption=question.value.trim();if(caption)body.append('caption',caption);
    const response=await fetch('/api/classroom/image',{method:'POST',headers:{'Accept':'application/json'},body});
    const data=await response.json();
    if(response.status===401){sessionToken=null;throw new Error('session');}
    if(!response.ok)throw new Error(data.detail||'request');
    showCanvasAnswer(data.reply,'Teaching response ready');
    thinking.textContent='I’ve placed the complete image explanation on the Teaching Canvas.';
    question.value='';
  }catch(err){
    const message=err.message&&!['request','session','Failed to fetch'].includes(err.message)?err.message:'I could not read that image. Please try a clearer photo.';
    thinking.textContent=message;canvasStatus.textContent='Image needs attention';
  }finally{uploadButton.disabled=false;cameraButton.disabled=false;imageUpload.value='';cameraCapture.value='';}
}

form.addEventListener('submit',async(e)=>{
  e.preventDefault();const text=question.value.trim();if(!text||sendButton.disabled)return;
  addMessage(text,'student');question.value='';sendButton.disabled=true;sendButton.textContent='Thinking…';
  const thinking=addMessage('Let me work through that with you…','teacher');
  try{
    const token=await ensureSession();
    const response=await fetch('/api/classroom/chat',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({message:text,session_token:token,language:language.value})});
    const data=await response.json();
    if(response.status===401){sessionToken=null;throw new Error('session');}
    if(!response.ok)throw new Error(data.detail||'request');
    canvasWork.classList.add('text-only');problemPreview.hidden=true;
    backToWhiteboard.classList.add('hidden');
    showCanvasAnswer(data.reply,'Worked solution');
    thinking.textContent='I’ve placed the complete worked solution on the Teaching Canvas.';
  }catch(err){
    thinking.textContent=err.message&&err.message.includes('wait')?err.message:'Sorry, I had a small technical hiccup. Please try your question again in a moment.';
  }finally{sendButton.disabled=false;sendButton.textContent='Send';question.focus()}
});
