const test=require('node:test');
const assert=require('node:assert/strict');
const {renderExampleReplay}=require('../classroom/example_replay.js');
class Node{
 constructor(doc,kind){this.ownerDocument=doc;this.kind=kind;this.children=[];this.attributes={};this.listeners={};this.classes=new Set();this.classList={add:k=>this.classes.add(k),toggle:(k,v)=>v?this.classes.add(k):this.classes.delete(k)};}
 appendChild(n){this.children.push(n);return n;}replaceChildren(){this.children=[];}setAttribute(k,v){this.attributes[k]=v;}removeAttribute(k){delete this.attributes[k];}addEventListener(k,f){this.listeners[k]=f;}click(){if(!this.disabled)this.listeners.click();}
}
function harness(texts=['First','Second','Third']){
 const doc={createElement:k=>new Node(doc,k)},container=new Node(doc,'div');
 let callback=null,cleared=0,started=0;
 const timers={setInterval(f){callback=f;started++;return 0;},clearInterval(){cleared++;callback=null;}};
 const player=renderExampleReplay(container,texts,timers);
 const controls=container.children.at(-1),[previous,play,next,restart,status]=controls.children;
 return {container,player,previous,play,next,restart,status,tick:()=>callback?.(),callback:()=>callback,counts:()=>({cleared,started})};
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
