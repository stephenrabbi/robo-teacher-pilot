const test=require('node:test');
const assert=require('node:assert/strict');
const {renderExampleReplay}=require('../classroom/example_replay.js');
class Node{
 constructor(doc,kind){this.ownerDocument=doc;this.kind=kind;this.children=[];this.attributes={};this.listeners={};this.classes=new Set();this.classList={add:k=>this.classes.add(k),toggle:(k,v)=>v?this.classes.add(k):this.classes.delete(k)};}
 appendChild(n){this.children.push(n);return n;}replaceChildren(){this.children=[];}setAttribute(k,v){this.attributes[k]=v;}removeAttribute(k){delete this.attributes[k];}addEventListener(k,f){this.listeners[k]=f;}click(){if(!this.disabled)this.listeners.click();}
}
function harness(texts=['First','Second','Third'],narration=null,startIndex=0){
 const doc={createElement:k=>new Node(doc,k)},container=new Node(doc,'div');
 let callback=null,cleared=0,started=0;
 const timers={setInterval(f){callback=f;started++;return 0;},clearInterval(){cleared++;callback=null;}};
 const player=renderExampleReplay(container,texts,timers,narration,startIndex);
 const controls=container.children.at(-1),[previous,play,next,restart]=controls.children,status=controls.children.at(-1);
 return {container,controls,player,previous,play,next,restart,status,tick:()=>callback?.(),callback:()=>callback,counts:()=>({cleared,started})};
}
test('examples start paused and manual navigation stays within bounds',()=>{
 const h=harness();assert.match(h.status.textContent,/1 of 3.*paused/);assert.equal(h.previous.disabled,true);assert.equal(h.counts().started,0);
 h.next.click();assert.match(h.status.textContent,/2 of 3.*paused/);h.previous.click();assert.match(h.status.textContent,/1 of 3/);
 h.next.click();h.next.click();assert.equal(h.next.disabled,true);assert.equal(h.play.disabled,true);assert.match(h.status.textContent,/complete/);
 h.restart.click();assert.match(h.status.textContent,/1 of 3.*paused/);
});
test('play advances once per tick, pause clears the timer, and completion does not loop',()=>{
 const h=harness();h.play.click();assert.equal(h.play.textContent,'Pause example');h.tick();assert.match(h.status.textContent,/2 of 3.*playing/);
 const late=h.callback();h.play.click();assert.equal(h.counts().cleared,1);late();h.tick();assert.match(h.status.textContent,/2 of 3.*paused/);
 h.play.click();h.tick();assert.match(h.status.textContent,/3 of 3.*complete/);assert.equal(h.counts().cleared,2);h.tick();assert.match(h.status.textContent,/3 of 3/);
});
test('closing the stage disposes playback and old controls cannot restart it',()=>{
 const h=harness();h.play.click();const late=h.callback();h.player.dispose();late();h.restart.click();h.play.click();assert.equal(h.counts().started,1);assert.equal(h.counts().cleared,1);assert.match(h.status.textContent,/1 of 3/);
});
test('single-step and empty examples do not create timers',()=>{
 const h=harness(['Only step']);assert.equal(h.play.disabled,true);assert.match(h.status.textContent,/complete/);assert.equal(h.counts().started,0);
 const e=harness([]);assert.match(e.container.children[0].textContent,/No example steps/);e.player.dispose();assert.equal(e.counts().started,0);
});

test('reading uses only the active step and manual navigation or disposal stops voice',()=>{
 const spoken=[];let stopped=0;
 const h=harness(['First explanation','Second explanation'],{read:t=>spoken.push(t),stop:()=>stopped++});
 h.play.click();h.controls.children[4].click();assert.deepEqual(spoken,['First explanation']);assert.match(h.status.textContent,/paused/);
 const before=stopped;h.next.click();assert.ok(stopped>before);
 h.controls.children[4].click();assert.deepEqual(spoken,['First explanation','Second explanation']);
 const last=stopped;h.controls.children[5].click();assert.ok(stopped>last);
 h.player.dispose();h.controls.children[4].click();assert.equal(spoken.length,2);
});

test('example question identifies the active step and restored playback stays paused',()=>{
 let asked;const h=harness(['Original first','Original second'],{read(){},stop(){},ask:(text,index)=>{asked={text,index}}},1);
 assert.match(h.status.textContent,/2 of 2.*complete/);h.controls.children[6].click();assert.deepEqual(asked,{text:'Original second',index:1});assert.equal(h.counts().started,0);
});

test('voice pause and continue follow actual audio state and cannot restart disposed audio',()=>{
 let pauses=0,resumes=0;const h=harness(['First','Second'],{read(){},stop(){},pause(){pauses++},resume(){resumes++}});
 const control=h.controls.children[6];assert.equal(control.disabled,true);
 h.player.setVoiceState('preparing');assert.equal(control.disabled,true);
 h.player.setVoiceState('speaking');assert.equal(control.disabled,false);control.click();assert.equal(pauses,1);
 h.player.setVoiceState('paused');assert.equal(control.textContent,'Continue example voice');control.click();assert.equal(resumes,1);
 h.player.setVoiceState('idle');assert.equal(control.disabled,true);
 h.player.dispose();h.player.setVoiceState('speaking');control.click();assert.equal(pauses,1);
});
test('voice navigation exposes the active step, respects bounds and stops after disposal',()=>{
 const h=harness(['One','Two']);h.player.moveBy(1);assert.deepEqual(h.player.getStep(),{text:'Two',index:1});
 h.player.moveBy(1);assert.equal(h.player.getStep().index,1);h.player.moveBy(-1);assert.equal(h.player.getStep().index,0);
 h.player.dispose();h.player.moveBy(1);assert.equal(h.player.getStep(),null);
});
