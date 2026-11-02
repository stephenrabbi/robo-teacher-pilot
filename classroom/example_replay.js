/* Learner-paced worked examples. Timers are disposed when the stage closes. */
(function(root){
  'use strict';
  function renderExampleReplay(container,texts,timers=root,narration=null){
    const doc=container.ownerDocument;container.replaceChildren();
    const values=Array.isArray(texts)?texts.filter(t=>typeof t==='string'&&t.trim()).slice(0,8):[];
    if(!values.length){const note=doc.createElement('p');note.textContent='No example steps are available. Return to the lesson and try again.';container.appendChild(note);return {dispose(){}};}
    let active=0,timer=null,disposed=false,generation=0;
    const steps=values.map((text,index)=>{const p=doc.createElement('p');p.textContent=`${index+1}. ${text}`;container.appendChild(p);return p;});
    const controls=doc.createElement('div');controls.classList.add('example-controls');
    const status=doc.createElement('span');status.setAttribute('role','status');status.setAttribute('aria-live','polite');
    const button=(label,action)=>{const b=doc.createElement('button');b.type='button';b.textContent=label;b.addEventListener('click',()=>{if(!disposed)action()});controls.appendChild(b);return b;};
    function stop(){if(narration)narration.stop();generation++;if(timer!==null){timers.clearInterval(timer);timer=null;}}
    function show(){
      steps.forEach((p,i)=>{p.classList.toggle('active',i===active);if(i===active)p.setAttribute('aria-current','step');else p.removeAttribute('aria-current');});
      previous.disabled=active===0;next.disabled=active===steps.length-1;
      play.textContent=timer===null?'Play example':'Pause example';play.disabled=active===steps.length-1;
      play.setAttribute('aria-pressed',String(timer!==null));
      status.textContent=`Example step ${active+1} of ${steps.length}${active===steps.length-1?' — complete':timer===null?' — paused':' — playing'}`;
    }
    const previous=button('Previous example step',()=>{stop();active=Math.max(0,active-1);show();});
    const play=button('Play example',()=>{if(timer!==null)stop();else if(active<steps.length-1){const owner=++generation;timer=timers.setInterval(()=>{if(disposed||owner!==generation)return;active++;if(active>=steps.length-1){active=steps.length-1;stop();}show();},2600);}show();});
    const next=button('Next example step',()=>{stop();active=Math.min(steps.length-1,active+1);show();});
    button('Restart example',()=>{stop();active=0;show();});
    if(narration){
      button('Read example step',()=>{stop();show();narration.read(values[active]);});
      button('Stop example voice',()=>{stop();show();});
    }
    controls.appendChild(status);container.appendChild(controls);show();
    return {dispose(){disposed=true;stop();}};
  }
  if(typeof module==='object'&&module.exports)module.exports={renderExampleReplay};
  else root.RoboTeacherExamples={renderExampleReplay};
})(typeof window==='undefined'?globalThis:window);
