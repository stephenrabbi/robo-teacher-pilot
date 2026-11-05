// Decode the real lesson video assets in a synthetic local page, with no AI calls.
const {chromium}=require('playwright'),fs=require('node:fs'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  const lessons = [
   {id:'adding-unlike-fractions', duration:54.25, minCues:10},
   {id:'adding-directed-numbers', duration:46.064, minCues:9},
  ];
  for(const {id,duration,minCues} of lessons) for(const width of [390,1280]){
   const page=await browser.newPage({viewport:{width,height:900}});
   await page.route('**/*',route=>{
    const u=new URL(route.request().url());
    if(u.origin!=='http://127.0.0.1:8765')return route.abort();
    if(u.pathname.startsWith('/api/'))return route.fulfill({status:503,json:{detail:'Synthetic media test'}});
    if(['.mp4','.webm'].some(ext=>u.pathname.endsWith('/'+id+ext))){
     const bytes=fs.readFileSync('.'+u.pathname),type=u.pathname.endsWith('.webm')?'video/webm':'video/mp4';
     const range=/^bytes=(\d+)-(\d*)$/.exec(route.request().headers().range||'');
     if(range){const start=Number(range[1]),end=Math.min(range[2]?Number(range[2]):bytes.length-1,bytes.length-1);return route.fulfill({status:206,contentType:type,headers:{'Accept-Ranges':'bytes','Content-Range':`bytes ${start}-${end}/${bytes.length}`},body:bytes.subarray(start,end+1)});}
     return route.fulfill({contentType:type,body:bytes});
    }
    return route.continue();
   });
   await page.goto('http://127.0.0.1:8765/classroom/index.html');
   await page.evaluate(id=>{
    const host=document.createElement('main');host.style.cssText='max-width:900px;margin:auto';document.body.replaceChildren(host);
    window.testEvents={};window.testHost=host;
    window.testPlayer=window.RoboTeacherVideos.renderTopicVideo(host,id,{ask:checkpoint=>window.testEvents.asked=checkpoint,continueTeacher:()=>window.testEvents.continued=true},24);
   },id);
   const video=page.locator('video');
   await page.waitForFunction(()=>{const v=document.querySelector('video');return v.readyState>=2&&Math.abs(v.currentTime-24)<.15;});
   assert.equal(await video.evaluate(v=>v.paused),true);
   assert.ok(Math.abs(await video.evaluate(v=>v.duration)-duration)<.2);
   await video.evaluate(async v=>{await v.play()});
   await page.waitForFunction(()=>document.querySelector('video').currentTime>24.25);
   await page.getByRole('button',{name:'Ask about this video',exact:true}).click();
   assert.equal(await video.evaluate(v=>v.paused),true);
   const saved=await page.evaluate(()=>window.testEvents.asked);
   assert.equal(saved.id,id);assert.ok(saved.time>24);
   await page.evaluate(saved=>{window.testPlayer.dispose();window.testPlayer=window.RoboTeacherVideos.renderTopicVideo(window.testHost,saved.id,{continueTeacher:()=>window.testEvents.continued=true},saved.time)},saved);
   await page.waitForFunction(t=>{const v=document.querySelector('video');return v.readyState>=2&&Math.abs(v.currentTime-t)<.15;},saved.time);
   assert.equal(await video.evaluate(v=>v.paused),true);
   await page.getByRole('button',{name:'Continue with teacher',exact:true}).click();
   assert.equal(await page.evaluate(()=>window.testEvents.continued),true);
   await page.waitForFunction(()=>document.querySelector('video').textTracks[0]?.cues?.length>0);
   assert.ok(await video.evaluate(v=>v.textTracks[0].cues.length)>=minCues);
   assert.equal(await video.evaluate(v=>v.error),null);
   await page.close();console.log(`${id} ${width}: decode, captions, paused restore, playback and handoff PASS`);
  }
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
