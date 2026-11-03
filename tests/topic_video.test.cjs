const test=require('node:test'),assert=require('node:assert/strict');
const {getTopicVideo,validCheckpoint,renderTopicVideo}=require('../classroom/topic_video.js');
test('saved video positions resolve through a fixed local catalog',()=>{
 assert.match(getTopicVideo('rounding-nearest-ten').src,/^\/classroom\/assets\/videos\//);
 for(const value of [null,{id:'https://example.com/x',time:10},{id:'__proto__',time:0},{id:'rounding-nearest-ten',time:-1},{id:'rounding-nearest-ten',time:Infinity}])assert.equal(validCheckpoint(value),false);
 assert.equal(validCheckpoint({id:'rounding-nearest-ten',time:12.25}),true);
});
test('video restore stays paused, clamps time, captures question position and disposes safely',()=>{
 const nodes=[];const doc={createElement(kind){const e={kind,children:[],listeners:{},currentTime:0,duration:41,paused:true,setAttribute(){},removeAttribute(){},appendChild(n){this.children.push(n)},append(...n){this.children.push(...n)},addEventListener(k,f){this.listeners[k]=f},pause(){this.paused=true},load(){this.loaded=true},play(){this.paused=false;return Promise.resolve()}};nodes.push(e);return e;}};
 const container={ownerDocument:doc,replaceChildren(){},append(){}};let asked,continued=0;
 const player=renderTopicVideo(container,'rounding-nearest-ten',{ask:v=>asked=v,continueTeacher:()=>continued++},900);const video=nodes.find(n=>n.kind==='video');
 video.listeners.loadedmetadata();assert.equal(video.currentTime,40.95);assert.equal(video.paused,true);
 video.currentTime=12.25;nodes.find(n=>n.kind==='button').listeners.click();assert.deepEqual(asked,{id:'rounding-nearest-ten',time:12.25});
 video.listeners.ended();assert.equal(continued,0);
 const continueButton=nodes.find(n=>n.textContent==='Continue with teacher');video.paused=false;continueButton.listeners.click();assert.equal(video.paused,true);assert.equal(continued,1);
 player.dispose();video.currentTime=1;video.listeners.loadedmetadata();assert.equal(video.currentTime,1);assert.equal(player.getCheckpoint(),null);assert.equal(video.loaded,true);
 continueButton.listeners.click();assert.equal(continued,1);
 assert.equal(renderTopicVideo(container,'https://example.com/x'),null);
});
