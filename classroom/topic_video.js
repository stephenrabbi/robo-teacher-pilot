/* Local, curated topic videos. Saved checkpoints contain IDs, never URLs. */
(function(root){
 'use strict';
 const catalog={
  'rounding-nearest-ten':{
   title:'Rounding to the nearest ten — worked example: 47',
   src:'/classroom/assets/videos/rounding-nearest-ten.mp4',
   webm:'/classroom/assets/videos/rounding-nearest-ten.webm',
   captions:'/classroom/assets/videos/rounding-nearest-ten.vtt',
   transcript:'Rounding means choosing the nearest multiple of ten. Let us round forty seven to the nearest ten. Forty seven lies between forty and fifty. The halfway point is forty five. Forty seven is above forty five, so it is closer to fifty. Move up to fifty. Forty seven rounded to the nearest ten is fifty. For whole numbers, a units digit of five or more rounds up; less than five rounds down.'
  }
 };
 function getTopicVideo(id){return Object.hasOwn(catalog,id)?catalog[id]:null;}
 function validCheckpoint(value){return Boolean(value&&getTopicVideo(value.id)&&Number.isFinite(value.time)&&value.time>=0&&value.time<=3600);}
 function renderTopicVideo(container,id,options={},start=0){
  const data=getTopicVideo(id);if(!data)return null;
  const doc=container.ownerDocument;container.replaceChildren();let disposed=false,lastSaved=0;
  const video=doc.createElement('video');video.controls=true;video.preload='metadata';video.playsInline=true;video.className='topic-video';video.setAttribute('aria-label',data.title);
  const sources=[];for(const [src,type] of [[data.webm,'video/webm'],[data.src,'video/mp4']]){const source=doc.createElement('source');source.src=src;source.type=type;sources.push(source);video.appendChild(source);}
  const track=doc.createElement('track');track.kind='captions';track.label='English';track.srclang='en';track.src=data.captions;track.default=true;video.appendChild(track);
  const status=doc.createElement('p');status.setAttribute('role','status');status.textContent='Play when you are ready. Use fullscreen for a larger diagram. Pause and ask a question at any time.';
  const checkpoint=()=>disposed?null:{id,time:Number.isFinite(video.currentTime)?video.currentTime:0};
  const save=()=>{if(!disposed)options.onCheckpoint?.(checkpoint());};
  video.addEventListener('loadedmetadata',()=>{if(disposed)return;if(Number.isFinite(start)&&start>0&&Number.isFinite(video.duration))video.currentTime=Math.min(start,Math.max(0,video.duration-.05));});
  video.addEventListener('pause',save);video.addEventListener('seeked',save);
  video.addEventListener('timeupdate',()=>{if(!disposed&&Math.abs(video.currentTime-lastSaved)>=5){lastSaved=video.currentTime;save();}});
  video.addEventListener('ended',()=>{if(disposed)return;status.textContent='Video complete. Ask a question or return to the explanation.';save();});
  video.addEventListener('error',()=>{if(!disposed)status.textContent='The video could not load. Read the transcript below or return to the explanation.';});
  const ask=doc.createElement('button');ask.type='button';ask.textContent='Ask about this video';ask.addEventListener('click',()=>{if(disposed)return;video.pause();options.ask?.(checkpoint());});
  const details=doc.createElement('details'),summary=doc.createElement('summary'),text=doc.createElement('p');summary.textContent='Read video transcript';text.textContent=data.transcript;details.append(summary,text);
  container.append(video,status,ask,details);
  return {getCheckpoint:checkpoint,pause(){if(!disposed)video.pause();},resume(){if(!disposed)void video.play().catch(()=>{if(!disposed)status.textContent='Tap Play on the video to continue.';});},moveBy(direction){if(!disposed&&Number.isFinite(video.duration))video.currentTime=Math.max(0,Math.min(video.duration,video.currentTime+direction*10));},dispose(){disposed=true;video.pause();video.removeAttribute('src');for(const source of sources)source.removeAttribute('src');video.load();}};
 }
 if(typeof module==='object'&&module.exports)module.exports={getTopicVideo,validCheckpoint,renderTopicVideo};
 else root.RoboTeacherVideos={getTopicVideo,validCheckpoint,renderTopicVideo};
})(typeof window==='undefined'?globalThis:window);
