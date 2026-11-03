// Synthetic PCM exercises the real playback-completion path; no external API calls.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required']});
 try{
  for(const width of [375,390,768,1280]){
   const page=await browser.newPage({viewport:{width,height:900}});const spoken=[];let fail=false;
   await page.route('**/*',route=>{
    const u=new URL(route.request().url());if(u.origin!=='http://127.0.0.1:8765')return route.abort();
    if(u.pathname==='/')return route.fulfill({json:{status:'ready'}});
    if(u.pathname==='/api/classroom/session')return route.fulfill({json:{session_token:'synthetic-narrated-example'}});
    if(u.pathname==='/api/classroom/media')return route.fulfill({json:{kind:'replay',title:'Synthetic explanation',source:'Robo-Teacher',steps:['First teaching step.','Second teaching step.','Final teaching step.']}});
    if(u.pathname==='/api/classroom/speech'){spoken.push(route.request().postDataJSON().text);return fail?route.fulfill({status:400,json:{detail:'Synthetic voice failure'}}):route.fulfill({contentType:'audio/L16',body:Buffer.alloc(48000)});}
    if(u.pathname.startsWith('/api/'))return route.fulfill({status:503,json:{detail:'Not used'}});
    return route.continue();
   });
   await page.goto('http://127.0.0.1:8765/classroom/index.html');
   if(await page.getByRole('button',{name:'Essential only',exact:true}).isVisible())await page.getByRole('button',{name:'Essential only',exact:true}).click();
   await page.evaluate(()=>window.eval("learnerNickname.value='SyntheticNarrationQA';enterClassroomView();canvasEmpty.classList.add('hidden');canvasWork.classList.remove('hidden');startLessonDirector('Original explanation',0,['Original exact lesson step']);"));
   await page.locator('#mediaButton').click();await page.getByRole('button',{name:'Read example from here',exact:true}).click();
   await page.waitForFunction(()=>document.querySelector('#mediaReplay [role=status]')?.textContent.includes('3 of 3 — complete'));
   assert.deepEqual(spoken,['First teaching step.','Second teaching step.','Final teaching step.']);
   assert.equal(await page.locator('#teacherPanel').evaluate(e=>e.classList.contains('speaking')),false);
   await page.getByRole('button',{name:'Restart example',exact:true}).click();
   await page.getByRole('button',{name:'Read example from here',exact:true}).click();
   await page.getByRole('button',{name:'Pause example voice',exact:true}).click();
   const count=spoken.length;await page.waitForTimeout(250);assert.equal(spoken.length,count);
   assert.match(await page.locator('#mediaReplay [role=status]').innerText(),/1 of 3/);
   await page.getByRole('button',{name:'Continue example voice',exact:true}).click();
   await page.getByRole('button',{name:'Stop narrated example',exact:true}).click();
   await page.waitForTimeout(1100);assert.equal(spoken.length,count);
   fail=true;await page.getByRole('button',{name:'Read example from here',exact:true}).click();
   await page.waitForFunction(()=>document.querySelector('#mediaReplay [role=status]')?.textContent.includes('1 of 3 — paused'));
   assert.equal(spoken.length,count+1);
   await page.getByRole('button',{name:'Exit example and return to the lesson',exact:true}).click();
   assert.equal(await page.locator('#canvasAnswer').innerText(),'Original exact lesson step');
   await page.close();console.log(width+': narrated order, playback completion, pause, cancellation, voice failure and lesson return PASS');
  }
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
