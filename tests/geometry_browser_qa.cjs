// Synthetic geometry acceptance; no external services or learner data.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true});let shape='rectangle';
 try{
  const page=await browser.newPage();
  await page.route('**/*',route=>{
   const url=new URL(route.request().url());if(url.origin!=='http://127.0.0.1:8765')return route.abort();
   if(url.pathname==='/')return route.fulfill({json:{status:'ready'}});
   if(url.pathname==='/api/classroom/session')return route.fulfill({json:{session_token:'synthetic-geometry-session-token'}});
   if(url.pathname==='/api/classroom/visual')return route.fulfill({json:{kind:'geometry',title:shape+' schematic',items:[{label:shape,value:1}],caption:'Schematic. Not to scale.'}});
   if(url.pathname.startsWith('/api/'))return route.fulfill({status:503,json:{detail:'Not used'}});
   return route.continue();
  });
  fs.mkdirSync('responsive-qa',{recursive:true});
  for(const width of [375,390,768,1280])for(shape of ['rectangle','circle','triangle']){
   await page.setViewportSize({width,height:900});await page.goto('http://127.0.0.1:8765/classroom/index.html');
   if(await page.getByRole('button',{name:'Essential only',exact:true}).isVisible())await page.getByRole('button',{name:'Essential only',exact:true}).click();
   await page.evaluate(()=>window.eval("learnerNickname.value='SyntheticGeometryQA';enterClassroomView();canvasEmpty.classList.add('hidden');canvasWork.classList.remove('hidden');startLessonDirector('Original geometry lesson',0,['Exact original geometry explanation']);"));
   await page.locator('#showStepVisual').click();await page.locator('.geometry-diagram').waitFor({state:'visible'});
   const box=await page.locator('.geometry-diagram').boundingBox();assert.ok(box.width>0&&box.x>=0&&box.x+box.width<=width);
   await page.getByRole('button',{name:'Hide shape labels',exact:true}).click();assert.equal(await page.locator('[data-geometry-labels]').getAttribute('visibility'),'hidden');
   await page.getByRole('button',{name:'Show shape labels',exact:true}).click();await page.getByRole('button',{name:'Show area formula',exact:true}).click();
   assert.match(await page.locator('#visualGraphic [role=status]').innerText(),/Area =/);
   await page.locator('#visualGraphic').screenshot({path:`responsive-qa/geometry-${shape}-${width}.png`});
   await page.getByRole('button',{name:'Return to explanation',exact:true}).click();assert.equal(await page.locator('#canvasAnswer').innerText(),'Exact original geometry explanation');
  }
  console.log('Rectangle/circle/triangle schematics, labels, area formulas and lesson return at four widths: PASS');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
