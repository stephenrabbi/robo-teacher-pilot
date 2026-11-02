// Synthetic graph acceptance in Chromium; no external services or real learners.
const {chromium}=require('playwright');
const fs=require('node:fs');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage();
  await page.route('**/*',route=>{
   const url=new URL(route.request().url());
   if(url.origin!=='http://127.0.0.1:8765')return route.abort();
   if(url.pathname==='/')return route.fulfill({json:{status:'synthetic ready'}});
   if(url.pathname==='/api/classroom/session')return route.fulfill({json:{session_token:'synthetic-graph-session-token'}});
   if(url.pathname==='/api/classroom/visual')return route.fulfill({json:{title:'Points on y = 2x + 1',kind:'coordinate',items:[{label:'-1,-1',value:1},{label:'0,1',value:2},{label:'1,3',value:3}],caption:'Three points from this synthetic lesson.'}});
   if(url.pathname.startsWith('/api/'))return route.fulfill({status:503,json:{detail:'Not used'}});
   return route.continue();
  });
  fs.mkdirSync('responsive-qa',{recursive:true});
  for(const width of [375,390,768,1280]){
   await page.setViewportSize({width,height:900});
   await page.goto('http://127.0.0.1:8765/classroom/index.html');
   await page.evaluate(()=>window.eval("learnerNickname.value='SyntheticGraphQA';enterClassroomView();canvasEmpty.classList.add('hidden');canvasWork.classList.remove('hidden');startLessonDirector('Plot (-1,-1), (0,1) and (1,3).',0,['Plot the given coordinates.']);"));
   await page.locator('#showStepVisual').click();
   await page.locator('.coordinate-graph').waitFor({state:'visible'});
   const box=await page.locator('.coordinate-graph').boundingBox();assert.ok(box.width>0&&box.x>=0&&box.x+box.width<=width);
   await page.getByRole('button',{name:'Plot step by step',exact:true}).click();
   await page.getByRole('button',{name:'Plot next point',exact:true}).click();
   assert.match(await page.locator('#visualGraphic [role=status]').innerText(),/Point A.*1 left.*1 down/);
   assert.equal(await page.locator('.coordinate-graph g[visibility=visible]').count(),1);
   assert.equal(await page.locator('.graph-point-table td').count(),9);
   await page.locator('.coordinate-graph').screenshot({path:`responsive-qa/coordinate-graph-${width}.png`});
   await page.getByRole('button',{name:'Show all points',exact:true}).click();
   assert.equal(await page.locator('.coordinate-graph g[visibility=visible]').count(),3);
   await page.getByRole('button',{name:'Return to explanation',exact:true}).click();
   assert.equal(await page.locator('#canvasAnswer').innerText(),'Plot the given coordinates.');
  }
  console.log('Guided coordinate plot, table and lesson return at 375/390/768/1280px: PASS');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1});
