/* Early subject workspace: no Maths lesson/progress writes and no HTML replies. */
(function(root){
 'use strict';
 function createSubjectClassroom(panel,options){
  const q=s=>panel.querySelector(s),select=q('#teachingSubject'),input=q('#subjectQuestion'),form=q('#subjectForm'),messages=q('#subjectMessages'),status=q('#subjectStatus'),send=q('#subjectSend'),upload=q('#subjectUpload'),file=q('#subjectFile'),mic=q('#subjectMic'),read=q('#subjectRead'),stop=q('#subjectStop'),starter=q('#subjectReadingStarter');
  let active=false,epoch=0,controller=null,conversation='',answer='',answerLanguage='',busy=false,recorder=null,stream=null,owner='';
  // NERDC English Studies reading objectives, printed pages 2, 25 and 49.
  const readingStarters={
   JSS1:['Find the main idea','Give me a short passage. Ask me to identify its main idea and one supporting detail. Wait for my answer before giving feedback.'],
   JSS2:["Explore the writer’s purpose","Give me a short passage. Ask me to identify the writer's purpose and one word or expression that supports it. Wait for my answer before giving feedback."],
   JSS3:['Spot facts and opinions','Give me a short passage containing facts and opinions. Ask me to classify one statement and explain my reason. Wait for my answer before giving feedback.'],
  };
  const fresh=()=>{const bytes=new Uint8Array(16);root.crypto.getRandomValues(bytes);return Array.from(bytes,b=>b.toString(16).padStart(2,'0')).join('');};
  const notice=(text,state='')=>{status.textContent=text;if(active)options.status?.(text,state);};
  const getAnswer=()=>!busy&&recorder?.state!=='recording'&&answerLanguage===options.language()?answer:'';
  function controls(){
   const locked=busy||recorder?.state==='recording';
   send.disabled=locked;
   upload.disabled=locked;
   input.disabled=locked;
   read.disabled=!getAnswer();
   options.answer?.(active?getAnswer():'');
   const reading=readingStarters[options.classLevel?.()];
   starter.hidden=select.value!=='English Language'||!reading;
   starter.textContent=reading?.[0]||'Try reading practice';
   starter.disabled=locked||!!input.value.trim();
  }
  function tracks(){if(stream){stream.getTracks().forEach(t=>t.stop());stream=null;}options.listening?.(false);}
  function cancel(){epoch++;controller?.abort();controller=null;const old=recorder;recorder=null;if(old&&old.state!=='inactive')old.stop();tracks();busy=false;mic.disabled=false;mic.textContent='Record question';options.stop?.();controls();}
  function reset(clear=true){cancel();conversation=fresh();answer='';answerLanguage='';if(clear){messages.replaceChildren();input.value='';}controls();notice(`Ask ${select.value==='English Language'?'an English Language':'a Basic Science'} question.`);}
  function append(label,text){const card=panel.ownerDocument.createElement('article'),heading=panel.ownerDocument.createElement('strong'),body=panel.ownerDocument.createElement('p');heading.textContent=label;if(label==='Your question')body.textContent=text;else{
   for(const [index,part] of text.split(/\*\*([^*\n]+)\*\*/g).entries()){
    if(index%2===0)body.append(part);
    else{const strong=panel.ownerDocument.createElement('strong');strong.textContent=part;body.append(strong);}
   }
  }card.append(heading,body);messages.appendChild(card);while(messages.children.length>12)messages.firstElementChild.remove();}
  async function request(kind,question,blob=null){
   if(!active||busy)return;
   if(kind!=='chat'&&question.length>500){notice('Please keep the caption under 500 characters, or send it as a typed question.','attention');return;}
   if(!conversation)conversation=fresh();options.stop?.();busy=true;controls();mic.disabled=true;
   const version=epoch,subject=select.value,language=options.language(),abort=new AbortController();controller=abort;
   const owns=()=>active&&version===epoch&&!abort.signal.aborted;
   notice('Preparing your explanation…','thinking');
   try{
    const token=await options.session();if(!owns())return;
    let body,headers;
    if(kind==='chat'){headers={'Content-Type':'application/json'};body=JSON.stringify({message:question,subject,language,conversation_id:conversation,session_token:token});}
    else{body=new FormData();for(const [key,value] of Object.entries({session_token:token,subject,language,conversation_id:conversation,caption:question}))body.append(key,value);body.append('file',blob,kind==='image'?'question-image':'question-recording');}
    const response=await root.fetch(`/api/classroom/subject/${kind}`,{method:'POST',headers,body,signal:abort.signal});const data=await response.json();if(!owns())return;
    if(response.status===401)options.invalidSession?.();
    if(!response.ok||typeof data.reply!=='string')throw Error('unavailable');
    append('Your question',question||(kind==='image'?'Image question':'Recorded question'));append(`${subject} · ${language}`,data.reply);
    answer=data.reply;answerLanguage=language;input.value='';notice('Explanation ready. You can ask a follow-up.');
    if(kind==='audio')options.speak?.(answer);
   }catch(error){if(owns())notice('I could not prepare that answer. Your typed question is kept; please try again.','attention');}
   finally{if(owns()){controller=null;busy=false;mic.disabled=false;controls();}}
  }
  input.addEventListener('input',controls);
  starter.addEventListener('click',()=>{
   const reading=readingStarters[options.classLevel?.()];
   if(!active||busy||recorder?.state==='recording'||input.value.trim()||select.value!=='English Language'||!reading)return;
   input.value=reading[1];controls();input.focus();
   notice('Your reading question is ready. Tap Ask teacher to begin.');
  });
  form.addEventListener('submit',event=>{event.preventDefault();const text=input.value.trim();if(text)void request('chat',text);});
  upload.addEventListener('click',()=>file.click());
  file.addEventListener('change',()=>{const blob=file.files?.[0];if(!blob)return;const kind=blob.type.startsWith('image/')?'image':'audio';const limit=kind==='image'?8:12;if(blob.size>limit*1024*1024){notice(`Choose a file smaller than ${limit} MB.`,'attention');file.value='';return;}if(kind==='audio')Promise.resolve(options.prepareAudio?.()).catch(()=>{});void request(kind,input.value.trim(),blob);file.value='';});
  mic.addEventListener('click',async()=>{
   if(recorder?.state==='recording'){recorder.stop();return;}
   if(busy)return;
   if(!root.navigator.mediaDevices?.getUserMedia||!root.MediaRecorder){notice('Recording is unavailable here. Type a question or upload a recording.','attention');return;}
   const version=epoch;options.stop?.();mic.disabled=true;
   try{
    await options.prepareAudio?.();const opened=await root.navigator.mediaDevices.getUserMedia({audio:true});if(!active||version!==epoch||busy){opened.getTracks().forEach(t=>t.stop());return;}stream=opened;
    const chunks=[],capture=new root.MediaRecorder(stream);recorder=capture;
    capture.addEventListener('dataavailable',event=>{if(event.data.size)chunks.push(event.data);});
    capture.addEventListener('stop',()=>{if(recorder===capture){tracks();recorder=null;mic.textContent='Record question';}if(active&&version===epoch){controls();const blob=new Blob(chunks,{type:(capture.mimeType||'audio/webm').split(';')[0]});if(blob.size&&blob.size<=12*1024*1024)void request('audio','',blob);else notice('The recording was empty or too large. Please try a shorter question.','attention');}});
    capture.addEventListener('error',()=>{if(active&&version===epoch){cancel();notice('Recording was interrupted. Please repeat or type the question.','attention');}});
    capture.start();controls();mic.textContent='Stop recording';options.listening?.(true);notice('Listening to your question…','listening');
   }catch(error){if(active&&version===epoch){tracks();notice('The microphone could not start. You can type or upload your question.','attention');}}
   finally{if(active&&version===epoch)mic.disabled=false;}
  });
  read.addEventListener('click',()=>{const text=getAnswer();if(active&&text){if(options.read)options.read();else options.speak?.(text);}});stop.addEventListener('click',()=>options.stop?.());
  select.addEventListener('change',()=>reset());
  return {
   open(key){active=true;if(owner!==key){owner=key;reset();}else{controls();notice(`Continue your ${select.value} conversation.`);}input.focus();},
   close(){active=false;cancel();mic.disabled=false;},
   reset(){active=false;owner='';reset();},
   languageChanged(){cancel();conversation=fresh();controls();notice('New replies will use the selected teaching language. Ask your question again to get a new-language answer.');},
   setReadState(state){read.textContent=state==='speaking'?'Pause subject answer':state==='paused'?'Continue subject answer':'Read subject answer';},
   isOpen(){return active;},getAnswer,
  };
 }
 if(typeof module==='object'&&module.exports)module.exports={createSubjectClassroom};else root.RoboTeacherSubjects={createSubjectClassroom};
})(typeof window==='undefined'?globalThis:window);
