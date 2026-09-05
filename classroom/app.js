const welcome=document.getElementById('welcome');
const classroom=document.getElementById('classroom');
const start=document.getElementById('startLearning');
const learnerNickname=document.getElementById('learnerNickname');
const learnerClass=document.getElementById('learnerClass');
const onboardingError=document.getElementById('onboardingError');
const learnerIdentity=document.getElementById('learnerIdentity');
const toggle=document.getElementById('toggleTeacher');
const teacherPanel=document.getElementById('teacherPanel');
const readAnswerButton=document.getElementById('readAnswer');
const teacherVoiceStatus=document.getElementById('teacherVoiceStatus');
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
const practiceCount=document.getElementById('practiceCount');
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
const practiceResults=document.getElementById('practiceResults');
const resultPercentage=document.getElementById('resultPercentage');
const resultScore=document.getElementById('resultScore');
const resultRecommendation=document.getElementById('resultRecommendation');
const missedReview=document.getElementById('missedReview');
const practiceAgainButton=document.getElementById('practiceAgain');
const changePracticeTopicButton=document.getElementById('changePracticeTopic');
const exitPracticeResultsButton=document.getElementById('exitPracticeResults');
const viewProgressFromResults=document.getElementById('viewProgressFromResults');
const progressButton=document.getElementById('progressButton');
const progressArea=document.getElementById('progressArea');
const progressLoading=document.getElementById('progressLoading');
const progressEmpty=document.getElementById('progressEmpty');
const progressDashboard=document.getElementById('progressDashboard');
const closeProgressButton=document.getElementById('closeProgress');
const emptyStartPractice=document.getElementById('emptyStartPractice');
const progressSessions=document.getElementById('progressSessions');
const progressQuestions=document.getElementById('progressQuestions');
const progressAverage=document.getElementById('progressAverage');
const progressStrongest=document.getElementById('progressStrongest');
const progressRecommendation=document.getElementById('progressRecommendation');
const weeklySessions=document.getElementById('weeklySessions');
const weeklyQuestions=document.getElementById('weeklyQuestions');
const weeklyScore=document.getElementById('weeklyScore');
const weeklyImprovement=document.getElementById('weeklyImprovement');
const practiceRecommendation=document.getElementById('practiceRecommendation');
const progressTopics=document.getElementById('progressTopics');
const recentSessions=document.getElementById('recentSessions');
const progressStorageNotice=document.getElementById('progressStorageNotice');
let currentPractice=null;
let currentPracticeSummary=null;
let currentProgress=null;
let sessionToken=null;
let previewUrl=null;
let mediaRecorder=null;
let micStream=null;
let recordedChunks=[];
let teacherSpeechController=null;
let teacherSpeechRequest=0;
let teacherAudioContext=null;
const teacherAudioSources=new Set();
let teacherStreamComplete=false;
let drawing=false;
let drawingTool='pen';
let boardHasInk=false;
const boardContext=whiteboard.getContext('2d');
const savedLanguage=localStorage.getItem('roboTeacherLanguage');
if(['English','Yoruba','Igbo','Hausa'].includes(savedLanguage))language.value=savedLanguage;
const savedNickname=localStorage.getItem('roboTeacherNickname')||'';
const savedClass=localStorage.getItem('roboTeacherClass')||'JSS2';
learnerNickname.value=savedNickname;
if(['JSS1','JSS2','JSS3'].includes(savedClass))learnerClass.value=savedClass;
const classTopics={
  JSS1:['Whole Numbers','Factors, Multiples & Roots','Fractions','Decimals & Approximation','Algebra','Geometry & Mensuration','Statistics & Probability'],
  JSS2:['Whole Numbers','Fractions','Algebra','Ratio & Percentage','Factors, Multiples & Roots','Decimals & Approximation','Directed Numbers','Commercial Arithmetic','Inequalities & Graphs','Geometry & Mensuration','Statistics & Probability'],
  JSS3:['Whole Numbers','Directed Numbers','Algebra','Ratio & Percentage','Commercial Arithmetic','Inequalities & Graphs','Geometry & Mensuration','Statistics & Probability']
};
function updatePracticeTopics(){
  const previous=practiceTopic.value;practiceTopic.replaceChildren(...classTopics[learnerClass.value].map(topic=>{const option=document.createElement('option');option.textContent=topic;return option}));
  if(classTopics[learnerClass.value].includes(previous))practiceTopic.value=previous;
}
updatePracticeTopics();learnerClass.addEventListener('change',updatePracticeTopics);

async function ensureSession(){
  if(sessionToken)return sessionToken;
  let learnerKey=localStorage.getItem('roboTeacherLearnerKey');
  if(!/^[a-f0-9]{32,64}$/.test(learnerKey||'')){
    const bytes=crypto.getRandomValues(new Uint8Array(24));learnerKey=Array.from(bytes,byte=>byte.toString(16).padStart(2,'0')).join('');
    localStorage.setItem('roboTeacherLearnerKey',learnerKey);
  }
  const response=await fetch('/api/classroom/session',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({learner_key:learnerKey,nickname:learnerNickname.value.trim(),class_level:learnerClass.value})});
  if(!response.ok)throw new Error('session');
  const data=await response.json();
  sessionToken=data.session_token;
  return sessionToken;
}

start.addEventListener('click',async()=>{
  const nickname=learnerNickname.value.trim();
  if(nickname.length<2){onboardingError.textContent='Please enter a nickname with at least 2 letters.';onboardingError.classList.remove('hidden');learnerNickname.focus();return}
  onboardingError.classList.add('hidden');start.disabled=true;start.textContent='Opening classroom…';
  localStorage.setItem('roboTeacherNickname',nickname);localStorage.setItem('roboTeacherClass',learnerClass.value);
  try{
    await ensureSession();learnerIdentity.textContent=`${nickname.toUpperCase()} · ${learnerClass.value} CLASSROOM`;
    welcome.classList.add('hidden');classroom.classList.remove('hidden');
    addMessage(`Welcome, ${nickname}! I’ll explain each lesson at ${learnerClass.value} level.`,'teacher');question.focus();
  }catch(_){onboardingError.textContent='I could not start the classroom connection. Please try again.';onboardingError.classList.remove('hidden')}
  finally{start.disabled=false;start.textContent='Start Learning Now →'}
});

toggle.addEventListener('click',()=>{
  const mini=teacherPanel.classList.toggle('minimized');
  classroom.classList.toggle('teacher-min',mini);
  toggle.textContent=mini?'↗':'↙';
  toggle.setAttribute('aria-label',mini?'Maximize teacher':'Minimize teacher');
  toggle.setAttribute('aria-expanded',String(!mini));
});

function prepareSpeechText(text){
  return text
    .replace(/\*\*/g,'')
    .replace(/\s*\n+\s*/g,'. ')
    .replace(/\s*([=:])\s*/g,' $1 ')
    .replace(/\s+/g,' ')
    .replace(/([A-Za-zÀ-ž0-9])$/u,'$1.')
    .trim();
}

function setTeacherSpeaking(speaking){
  teacherPanel.classList.toggle('speaking',speaking);
  teacherVoiceStatus.textContent=speaking?'Speaking…':'Ready';
  readAnswerButton.innerHTML=speaking?'■ <span>Stop</span>':'🔊 <span>Read answer</span>';
  readAnswerButton.setAttribute('aria-label',speaking?'Stop reading the answer':'Read the current answer aloud');
}

function stopTeacherAudio(){
  teacherSpeechRequest+=1;
  if(teacherSpeechController){teacherSpeechController.abort();teacherSpeechController=null}
  teacherAudioSources.forEach(source=>{try{source.stop()}catch(_error){/* Already stopped. */}});teacherAudioSources.clear();
  if(teacherAudioContext){teacherAudioContext.close().catch(()=>{});teacherAudioContext=null}
  teacherStreamComplete=false;
  setTeacherSpeaking(false);
}

async function playPcmStream(response,requestId){
  const AudioContextClass=window.AudioContext||window.webkitAudioContext;
  if(!AudioContextClass)throw new Error('Web Audio is unavailable');
  teacherAudioContext=new AudioContextClass({sampleRate:24000});await teacherAudioContext.resume();
  const context=teacherAudioContext;const reader=response.body.getReader();let pending=new Uint8Array(0);let nextStart=context.currentTime+.06;
  const finishIfDone=()=>{if(teacherStreamComplete&&!teacherAudioSources.size&&requestId===teacherSpeechRequest)stopTeacherAudio()};
  while(requestId===teacherSpeechRequest){
    const {done,value}=await reader.read();if(done)break;
    const joined=new Uint8Array(pending.length+value.length);joined.set(pending);joined.set(value,pending.length);
    const evenLength=joined.length-joined.length%2;pending=joined.slice(evenLength);
    if(!evenLength)continue;
    const samples=evenLength/2;const buffer=context.createBuffer(1,samples,24000);const channel=buffer.getChannelData(0);const view=new DataView(joined.buffer,joined.byteOffset,evenLength);
    for(let index=0;index<samples;index++)channel[index]=view.getInt16(index*2,true)/32768;
    const source=context.createBufferSource();source.buffer=buffer;source.connect(context.destination);teacherAudioSources.add(source);
    source.addEventListener('ended',()=>{teacherAudioSources.delete(source);finishIfDone()},{once:true});
    const startAt=Math.max(nextStart,context.currentTime+.025);source.start(startAt);nextStart=startAt+buffer.duration;
  }
  teacherStreamComplete=true;finishIfDone();
}

async function speakText(text){
  if(!text.trim())return;
  stopTeacherAudio();setTeacherSpeaking(true);
  const requestId=teacherSpeechRequest;
  teacherSpeechController=new AbortController();
  try{
    const token=await ensureSession();
    if(requestId!==teacherSpeechRequest)return;
    const response=await fetch('/api/classroom/speech',{method:'POST',headers:{'Content-Type':'application/json','Accept':'audio/L16'},body:JSON.stringify({text:prepareSpeechText(text),session_token:token,language:language.value,voice_gender:teacherPanel.dataset.voiceGender==='male'?'male':'female'}),signal:teacherSpeechController.signal});
    if(response.status===401){sessionToken=null;throw new Error('session')}
    if(!response.ok)throw new Error('natural voice unavailable');
    if(!response.body)throw new Error('stream unavailable');
    await playPcmStream(response,requestId);
  }catch(error){
    if(error.name==='AbortError'||requestId!==teacherSpeechRequest)return;
    stopTeacherAudio();
    addMessage('The natural teacher voice is temporarily unavailable. You can continue reading the worked answer on the Teaching Canvas.','teacher');
  }
}

readAnswerButton.addEventListener('click',()=>{
  if(teacherPanel.classList.contains('speaking')){stopTeacherAudio();return;}
  speakText(canvasAnswer.textContent);
});

function addMessage(text,role){
  const el=document.createElement('div');el.className=`message ${role}`;el.textContent=text;
  messages.appendChild(el);messages.scrollTop=messages.scrollHeight;return el;
}

function showCanvasAnswer(answer,status='Worked solution'){
  whiteboardArea.classList.add('hidden');practiceArea.classList.add('hidden');progressArea.classList.add('hidden');canvasEmpty.classList.add('hidden');canvasWork.classList.remove('hidden');
  canvasStatus.textContent=status;renderLesson(canvasAnswer,answer);
  readAnswerButton.disabled=!answer.trim();
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
practiceAgainButton.addEventListener('click',startPracticeSession);
changePracticeTopicButton.addEventListener('click',resetPracticeSetup);
exitPracticeResultsButton.addEventListener('click',closePractice);
progressButton.addEventListener('click',openProgress);
viewProgressFromResults.addEventListener('click',openProgress);
closeProgressButton.addEventListener('click',closeProgress);
emptyStartPractice.addEventListener('click',openPracticeFromProgress);
practiceRecommendation.addEventListener('click',openRecommendedPractice);

function openPractice(){
  whiteboardArea.classList.add('hidden');progressArea.classList.add('hidden');canvasWork.classList.add('hidden');canvasEmpty.classList.add('hidden');practiceArea.classList.remove('hidden');
  if(currentPracticeSummary)renderPracticeResults(currentPracticeSummary);
  else if(currentPractice){practiceSetup.classList.add('hidden');practiceQuestion.classList.remove('hidden');practiceResults.classList.add('hidden');practiceAnswer.focus()}
  else resetPracticeSetup();
}

function closePractice(){
  practiceArea.classList.add('hidden');
  if(canvasAnswer.textContent.trim())canvasWork.classList.remove('hidden');else canvasEmpty.classList.remove('hidden');
}

function renderPracticeQuestion(data){
  currentPractice=data;currentPracticeSummary=null;practiceSetup.classList.add('hidden');practiceResults.classList.add('hidden');practiceQuestion.classList.remove('hidden');
  practiceProgress.textContent=`Question ${data.question_number} of ${data.total_questions}`;practiceScore.textContent=`Score: ${data.score}/${data.attempted}`;
  practiceContext.textContent=`${data.topic} · ${data.difficulty}`;practicePrompt.textContent=data.question;
  practiceAnswer.value='';practiceAnswer.disabled=false;practiceForm.querySelector('button').disabled=false;
  practiceFeedback.textContent='';practiceFeedback.className='practice-feedback hidden';showHintButton.disabled=false;
  showHintButton.textContent='Show Hint';nextPracticeButton.textContent='Next Question →';nextPracticeButton.classList.add('hidden');practiceAnswer.focus();
}

async function practiceRequest(path,body){
  const token=await ensureSession();
  const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),20000);
  try{
    const response=await fetch(`/api/classroom/practice/${path}`,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({session_token:token,...body}),signal:controller.signal});
    let data={};try{data=await response.json()}catch(_error){/* Use the friendly fallback below. */}
    if(response.status===401)sessionToken=null;if(!response.ok)throw new Error(data.detail||'Practice request failed. Please try again.');return data;
  }catch(error){if(error.name==='AbortError')throw new Error('The connection took too long. Please try again.');throw error}
  finally{clearTimeout(timeout)}
}

async function startPracticeSession(){
  startPracticeButton.disabled=true;practiceAgainButton.disabled=true;startPracticeButton.textContent='Preparing…';
  try{renderPracticeQuestion(await practiceRequest('start',{topic:practiceTopic.value,difficulty:practiceDifficulty.value,question_count:Number(practiceCount.value),class_level:learnerClass.value}))}
  catch(err){addMessage(err.message,'teacher')}
  finally{startPracticeButton.disabled=false;practiceAgainButton.disabled=false;startPracticeButton.textContent='Start Practice →'}
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
    practiceFeedback.textContent=result.correct?`${result.message}\n\n${result.explanation}`:`${result.message}\n\n${result.explanation}\n\nCorrect answer: ${result.expected_answer}`;
    practiceFeedback.className=`practice-feedback ${result.correct?'correct':'incorrect'}`;nextPracticeButton.classList.remove('hidden');showHintButton.disabled=true;
    if(result.completed){currentPracticeSummary=result.summary;nextPracticeButton.textContent='View Results →'}
  }catch(err){practiceFeedback.textContent=err.message;practiceFeedback.className='practice-feedback incorrect';checkButton.disabled=false}
}

async function loadNextPracticeQuestion(){
  if(currentPracticeSummary){renderPracticeResults(currentPracticeSummary);return}
  nextPracticeButton.disabled=true;
  try{renderPracticeQuestion(await practiceRequest('next',{}))}
  catch(err){practiceFeedback.textContent=err.message;practiceFeedback.className='practice-feedback incorrect'}
  finally{nextPracticeButton.disabled=false}
}

function resetPracticeSetup(){
  currentPractice=null;currentPracticeSummary=null;practiceQuestion.classList.add('hidden');practiceResults.classList.add('hidden');practiceSetup.classList.remove('hidden');
}

function renderPracticeResults(summary){
  currentPracticeSummary=summary;practiceSetup.classList.add('hidden');practiceQuestion.classList.add('hidden');practiceResults.classList.remove('hidden');
  resultPercentage.textContent=`${summary.percentage}%`;resultScore.textContent=`${summary.score} out of ${summary.attempted} correct`;
  resultRecommendation.textContent=summary.recommendation;missedReview.replaceChildren();
  const heading=document.createElement('h4');heading.textContent=summary.missed.length?'Questions to review':'Perfect score!';missedReview.appendChild(heading);
  if(!summary.missed.length){const note=document.createElement('p');note.textContent='You answered every question correctly. Excellent work!';missedReview.appendChild(note);return}
  summary.missed.forEach((item,index)=>{
    const card=document.createElement('article');
    const title=document.createElement('strong');title.textContent=`${index+1}. ${item.question}`;
    const answers=document.createElement('p');answers.textContent=`Your answer: ${item.learner_answer || 'No answer'} · Correct answer: ${item.correct_answer}`;
    const explanation=document.createElement('p');explanation.textContent=item.explanation;
    card.append(title,answers,explanation);missedReview.appendChild(card);
  });
}

async function openProgress(){
  whiteboardArea.classList.add('hidden');practiceArea.classList.add('hidden');canvasWork.classList.add('hidden');canvasEmpty.classList.add('hidden');progressArea.classList.remove('hidden');
  progressLoading.classList.remove('hidden');progressEmpty.classList.add('hidden');progressDashboard.classList.add('hidden');
  try{currentProgress=await practiceRequest('progress',{class_level:learnerClass.value});renderProgress(currentProgress)}
  catch(error){progressLoading.textContent=error.message;progressLoading.classList.add('error')}
}

function renderProgress(data){
  progressLoading.classList.add('hidden');progressLoading.classList.remove('error');
  if(!data.sessions){progressEmpty.classList.remove('hidden');return}
  progressDashboard.classList.remove('hidden');progressSessions.textContent=data.sessions;progressQuestions.textContent=data.total_questions;
  progressAverage.textContent=`${data.average_percentage}%`;progressStrongest.textContent=data.strongest_topic||'—';progressRecommendation.textContent=data.recommendation;
  const week=data.weekly_summary;weeklySessions.textContent=`${week.sessions} session${week.sessions===1?'':'s'}`;weeklyQuestions.textContent=`${week.questions} question${week.questions===1?'':'s'}`;weeklyScore.textContent=`${week.percentage}%`;
  weeklyImprovement.textContent=week.improvement_points===null?'Complete another week to measure improvement.':week.improvement_points>0?`Improved by ${week.improvement_points} percentage points.`:week.improvement_points<0?`Down ${Math.abs(week.improvement_points)} points—review the recommended topic.`:'Your score is steady compared with last week.';
  progressStorageNotice.classList.toggle('hidden',data.storage_synced);progressTopics.replaceChildren();recentSessions.replaceChildren();
  data.topics.forEach(item=>{
    const row=document.createElement('article');const label=document.createElement('div');const name=document.createElement('strong');const score=document.createElement('span');
    name.textContent=item.topic;score.textContent=`${item.percentage}% · ${item.correct}/${item.attempted}`;label.append(name,score);
    const track=document.createElement('div');track.className='progress-track';const fill=document.createElement('i');fill.style.width=`${item.percentage}%`;track.appendChild(fill);row.append(label,track);progressTopics.appendChild(row);
  });
  data.recent_sessions.forEach(item=>{
    const row=document.createElement('article');const detail=document.createElement('div');const topic=document.createElement('strong');const meta=document.createElement('span');const score=document.createElement('b');
    topic.textContent=item.topic;meta.textContent=`${item.difficulty} · ${formatProgressDate(item.timestamp)}`;score.textContent=`${item.percentage}%`;detail.append(topic,meta);row.append(detail,score);recentSessions.appendChild(row);
  });
}

function formatProgressDate(value){
  const date=new Date(value);return Number.isNaN(date.getTime())?'Completed':date.toLocaleDateString(undefined,{day:'numeric',month:'short'});
}

function closeProgress(){
  progressArea.classList.add('hidden');if(canvasAnswer.textContent.trim())canvasWork.classList.remove('hidden');else canvasEmpty.classList.remove('hidden');
}

function openPracticeFromProgress(){resetPracticeSetup();openPractice()}

function openRecommendedPractice(){
  resetPracticeSetup();updatePracticeTopics();
  if(currentProgress&&classTopics[learnerClass.value].includes(currentProgress.recommended_topic)){practiceTopic.value=currentProgress.recommended_topic;practiceDifficulty.value=currentProgress.recommended_difficulty}
  openPractice();
}

function clearWhiteboard(){
  boardContext.save();boardContext.fillStyle='#ffffff';boardContext.fillRect(0,0,whiteboard.width,whiteboard.height);boardContext.restore();
  boardHasInk=false;
}

function openWhiteboard(){
  canvasEmpty.classList.add('hidden');canvasWork.classList.add('hidden');practiceArea.classList.add('hidden');progressArea.classList.add('hidden');whiteboardArea.classList.remove('hidden');
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
    // A learner starting a new question always interrupts the current answer.
    stopTeacherAudio();
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
    // Start reading as soon as the written voice answer reaches the canvas.
    void speakText(data.reply);
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
