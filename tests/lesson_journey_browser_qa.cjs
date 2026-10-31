// Isolated browser acceptance: synthetic learner, local server, mocked APIs.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:375,height:850}});
  await page.route('**/*',async route=>{
   const url=new URL(route.request().url());
   if(url.origin!=='http://127.0.0.1:8765')return route.abort();
   if(url.pathname==='/')return route.fulfill({json:{status:'synthetic ready'}});
   if(url.pathname==='/api/classroom/session')return route.fulfill({json:{session_token:'synthetic-browser-session-token'}});
   if(url.pathname==='/api/classroom/chat')return route.fulfill({json:{reply:'Synthetic follow-up answer.'}});
   if(url.pathname.startsWith('/api/'))return route.fulfill({status:503,json:{detail:'Not used in this isolated test'}});
   return route.continue();
  });
  await page.goto('http://127.0.0.1:8765/classroom/index.html');
  await page.evaluate(()=>window.eval(`
    learnerNickname.value='QA Learner';learnerCode.value='TEST-CHECKPOINT';
    enterClassroomView();canvasEmpty.classList.add('hidden');canvasWork.classList.remove('hidden');
    startLessonDirector('Original synthetic lesson',1,['Introduction','Exact original graph step','Understanding check']);
  `));
  await page.locator('#askLessonQuestion').click();
  await page.locator('#question').fill('Why is that point on the line?');
  await page.locator('#chatForm button[type=submit]').click();
  await page.waitForFunction(()=>document.querySelector('#returnToLesson')&&!document.querySelector('#returnToLesson').classList.contains('hidden'));
  await page.locator('#askLessonQuestion').click();
  await page.locator('#question').fill('Can you explain that again?');
  await page.locator('#chatForm button[type=submit]').click();
  await page.waitForFunction(()=>document.querySelector('#question').value==='' && !document.querySelector('#chatForm button[type=submit]').disabled);
  await page.reload();
  await page.locator('#learnerConsent').check();
  await page.locator('#resumeLearning').click();
  await page.locator('#returnToLesson').waitFor({state:'visible'});
  await page.locator('#returnToLesson').click();
  await page.locator('#returnToLesson').click();
  assert.equal(await page.locator('#canvasAnswer').innerText(),'Exact original graph step');
  assert.equal(await page.locator('#lessonStepLabel').innerText(),'Step 2 of 3');
  assert.equal(await page.locator('#returnToLesson').isVisible(),false);
  await page.locator('#changeLearner').click();
  const cleared=await page.evaluate(()=>window.eval(`({history:lessonHistory.length,lesson:currentLesson,pending:pendingChatRecovery})`));
  assert.equal(cleared.history,0);assert.equal(cleared.lesson,null);assert.equal(cleared.pending,null);
  console.log('Nested questions, reload, exact-step return and learner reset: PASS');
 }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exitCode=1});
