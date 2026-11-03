// Isolated synthetic learners: workspace boundaries, stale replies and media.
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required']});
 try{
  fs.mkdirSync('responsive-qa',{recursive:true});
  for(const width of [375,390,768,1280]){
   const page=await browser.newPage({viewport:{width,height:900}}),sent=[],media=[],spoken=[],errors=[];let delayed=null;
   page.on('pageerror',e=>errors.push(e.message));
   await page.route('**/*',route=>{
    const u=new URL(route.request().url());if(u.origin!=='http://127.0.0.1:8765')return route.abort();
    if(u.pathname==='/')return route.fulfill({json:{status:'ready'}});
    if(u.pathname==='/api/classroom/session')return route.fulfill({json:{session_token:'synthetic-subject-session'}});
    if(u.pathname==='/api/classroom/subject/chat'){
     const data=route.request().postDataJSON();sent.push(data);
     if(data.message==='Delayed question'){delayed=route;return;}
     return route.fulfill({json:{reply:data.subject==='Basic Science'?'Plants use light to make food.':'A noun names a person, place or thing.'}});
    }
    if(['/api/classroom/subject/image','/api/classroom/subject/audio'].includes(u.pathname)){
     media.push({path:u.pathname,body:route.request().postDataBuffer().toString()});return route.fulfill({json:{reply:'Educational media explanation.'}});
    }
    if(u.pathname==='/api/classroom/speech'){spoken.push(route.request().postDataJSON().text);return route.fulfill({contentType:'audio/L16',body:Buffer.alloc(96000)});}
    if(u.pathname.startsWith('/api/'))return route.fulfill({status:503,json:{detail:'Not used'}});
    return route.continue();
   });
   await page.goto('http://127.0.0.1:8765/classroom/index.html');
   if(await page.getByRole('button',{name:'Essential only',exact:true}).isVisible())await page.getByRole('button',{name:'Essential only',exact:true}).click();
   await page.evaluate(()=>window.eval("learnerNickname.value='SyntheticSubjectQA';learnerCode.value='TEST-SUBJECT-QA';enterClassroomView();canvasEmpty.classList.add('hidden');canvasWork.classList.remove('hidden');startLessonDirector('Original Maths lesson',0,['Original Maths step retained']);"));
   await page.locator('#subjectsButton').click();await page.locator('#subjectLearning').waitFor({state:'visible'});
   await page.locator('#subjectQuestion').fill('Explain nouns');await page.locator('#subjectSend').click();
   await page.locator('#subjectRead').waitFor({state:'visible'});await page.waitForFunction(()=>!document.querySelector('#subjectRead').disabled);
   assert.equal(sent.at(-1).subject,'English Language');const firstId=sent.at(-1).conversation_id;
   await page.locator('#subjectRead').click();await page.waitForFunction(()=>document.querySelector('#teacherPanel').classList.contains('speaking'));
   assert.equal(spoken.at(-1),'A noun names a person, place or thing.');await page.locator('#subjectStop').click();
   await page.locator('#subjectQuestion').fill('Delayed question');await page.locator('#subjectSend').click();
   await page.waitForTimeout(100);assert.ok(delayed);
   await page.locator('#teachingSubject').selectOption('Basic Science');
   await delayed.fulfill({json:{reply:'STALE ENGLISH ANSWER'}}).catch(()=>{});await page.waitForTimeout(100);
   assert.equal(await page.locator('#subjectMessages').innerText(),'');
   await page.locator('#subjectQuestion').fill('How do plants feed?');await page.locator('#subjectSend').click();
   await page.waitForFunction(()=>document.querySelector('#subjectMessages').textContent.includes('Plants use light'));
   assert.equal(sent.at(-1).subject,'Basic Science');assert.notEqual(sent.at(-1).conversation_id,firstId);
   await page.locator('#subjectFile').setInputFiles({name:'plant.png',mimeType:'image/png',buffer:Buffer.from('synthetic educational image')});
   await page.waitForFunction(()=>document.querySelector('#subjectMessages').textContent.includes('Educational media explanation.'));
   assert.match(media.at(-1).body,/Basic Science/);
   await page.waitForFunction(()=>!document.querySelector('#subjectSend').disabled);
   await page.locator('#subjectFile').setInputFiles({name:'question.webm',mimeType:'audio/webm',buffer:Buffer.from('synthetic educational recording')});
   await page.waitForTimeout(200);assert.equal(media.at(-1).path,'/api/classroom/subject/audio');
   await page.locator('#subjectStop').click();await page.waitForFunction(()=>!document.querySelector('#subjectSend').disabled);
   await page.locator('#language').selectOption('Yoruba');
   assert.equal(await page.locator('#subjectRead').isDisabled(),true);
   await page.locator('#subjectQuestion').fill('Explain light');await page.locator('#subjectSend').click();await page.waitForFunction(()=>!document.querySelector('#subjectSend').disabled);
   assert.equal(sent.at(-1).language,'Yoruba');
   await page.locator('#subjectLearning').screenshot({path:`responsive-qa/subjects-${width}.png`});
   const box=await page.locator('#subjectLearning').boundingBox();assert.ok(box.x>=0&&box.x+box.width<=width+1);
   await page.locator('#subjectBack').click();assert.equal(await page.locator('#canvasAnswer').innerText(),'Original Maths step retained');
   await page.locator('#subjectsButton').click();await page.locator('#changeLearner').click();
   assert.equal(await page.locator('#subjectMessages').innerText(),'');assert.deepEqual(errors,[]);
   await page.close();console.log(`Subject workspace ${width}px passed`);
  }
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1);});
