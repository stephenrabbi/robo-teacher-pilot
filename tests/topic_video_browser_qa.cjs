// Actual local MP4 playback and recovery; no remote content or learner records.
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required']});
 try{
  fs.mkdirSync('responsive-qa',{recursive:true});
  for(const width of [375,390,768,1280]){
   const page=await browser.newPage({viewport:{width,height:900}});const questions=[];
   await page.route('**/*',route=>{
    const u=new URL(route.request().url());if(u.origin!=='http://127.0.0.1:8765')return route.abort();
    if(u.pathname==='/')return route.fulfill({json:{status:'ready'}});
    if(u.pathname==='/api/classroom/session')return route.fulfill({json:{session_token:'synthetic-topic-video-session'}});
    if(u.pathname==='/api/classroom/media')return route.fulfill({json:{kind:'video',video_id:'rounding-nearest-ten',title:'Rounding to the nearest ten — worked example: 47',source:'Robo-Teacher'}});
    if(u.pathname==='/api/classroom/chat'){questions.push(route.request().postDataJSON().message);return route.fulfill({json:{reply:'47 is closer to 50 because its distance from 50 is 3, while its distance from 40 is 7.'}});}
    // The simple CI HTTP server lacks Range support; serve the real encoded
    // assets with byte ranges, matching production's static-file server.
    if(['/classroom/assets/videos/rounding-nearest-ten.webm','/classroom/assets/videos/rounding-nearest-ten.mp4'].includes(u.pathname)){
     const bytes=fs.readFileSync('.'+u.pathname),type=u.pathname.endsWith('.webm')?'video/webm':'video/mp4';
     const range=/^bytes=(\d+)-(\d*)$/.exec(route.request().headers().range||'');
     if(range){const start=Number(range[1]),end=Math.min(range[2]?Number(range[2]):bytes.length-1,bytes.length-1);return route.fulfill({status:206,contentType:type,headers:{'Accept-Ranges':'bytes','Content-Range':`bytes ${start}-${end}/${bytes.length}`},body:bytes.subarray(start,end+1)});}
     return route.fulfill({contentType:type,headers:{'Accept-Ranges':'bytes'},body:bytes});
    }
    if(u.pathname.startsWith('/api/'))return route.fulfill({status:503,json:{detail:'Not used'}});
    return route.continue();
   });
   await page.goto('http://127.0.0.1:8765/classroom/index.html');
   if(await page.getByRole('button',{name:'Essential only',exact:true}).isVisible())await page.getByRole('button',{name:'Essential only',exact:true}).click();
   await page.evaluate(()=>window.eval("learnerNickname.value='SyntheticVideoQA';learnerCode.value='TEST-VIDEO-QA';enterClassroomView();canvasEmpty.classList.add('hidden');canvasWork.classList.remove('hidden');startLessonDirector('Round 47 to the nearest ten.',0,['Original exact rounding explanation']);"));
   await page.locator('#mediaButton').click();const video=page.locator('#mediaReplay video');
   await video.waitFor({state:'visible'});await page.waitForFunction(()=>{const v=document.querySelector('#mediaReplay video');if(v?.error)throw Error('Video decode failed: '+v.error.code);return v&&v.readyState>=1;},{},{timeout:15000});
   assert.equal(await video.evaluate(v=>v.paused),true);assert.ok(await video.evaluate(v=>v.duration>40&&v.duration<43));
   await video.evaluate(v=>v.play());await page.waitForTimeout(250);assert.ok(await video.evaluate(v=>v.currentTime>0));
   await video.evaluate(v=>{v.pause();v.currentTime=12.25;});await page.waitForFunction(()=>Math.abs(document.querySelector('#mediaReplay video').currentTime-12.25)<.1);
   await page.locator('#mediaArea').screenshot({path:`responsive-qa/topic-video-${width}.png`});
   const box=await video.boundingBox();assert.ok(box.width>0&&box.x>=0&&box.x+box.width<=width);
   await page.getByRole('button',{name:'Ask about this video',exact:true}).click();assert.equal(await video.count(),1);assert.equal(await page.locator('#mediaArea').isVisible(),false);
   await page.locator('#askLessonQuestion').click();
   await page.waitForFunction(()=>{const v=document.querySelector('#mediaReplay video');return v&&v.readyState>=1&&Math.abs(v.currentTime-12.25)<.1;});
   assert.equal(await page.locator('#mediaReplay video').evaluate(v=>v.paused),true);
   await page.getByRole('button',{name:'Ask about this video',exact:true}).click();
   await page.locator('#question').fill('Why is 47 closer to 50?');await page.locator('#chatForm button[type=submit]').click();
   await page.locator('#returnToLesson').waitFor({state:'visible'});assert.match(questions.at(-1),/Video paused at 12 seconds/);
   await page.locator('#returnToLesson').click();
   await page.waitForFunction(()=>{const v=document.querySelector('#mediaReplay video');return v&&v.readyState>=1&&Math.abs(v.currentTime-12.25)<.1;});
   await page.locator('#mediaReplay video').evaluate(v=>{v.currentTime=18.5;});
   await page.waitForFunction(()=>Math.abs(JSON.parse(localStorage.getItem('roboTeacherClassroomSnapshot')).topicVideo.time-18.5)<.1);
   await page.reload();await page.locator('#learnerConsent').check();await page.locator('#resumeLearning').click();
   await page.waitForFunction(()=>{const v=document.querySelector('#mediaReplay video');return v&&v.readyState>=1&&Math.abs(v.currentTime-18.5)<.1;});
   assert.equal(await page.locator('#mediaReplay video').evaluate(v=>v.paused),true);
   await page.getByRole('button',{name:'Exit video and return to the lesson',exact:true}).click();
   assert.equal(await page.locator('#canvasAnswer').innerText(),'Original exact rounding explanation');
   assert.equal(await page.locator('#teacherPanel').getAttribute('data-pose'),'portrait');
   await page.close();console.log(width+': actual MP4, timestamp question return, paused reload recovery, original lesson return PASS');
  }
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
