const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  fs.mkdirSync('responsive-qa',{recursive:true});
  for(const width of [375,390,768,1280]){
   const page=await browser.newPage({viewport:{width,height:900}});
   await page.goto('http://127.0.0.1:8765/classroom/previews/presenter.html');
   assert.equal(await page.locator('.presenter img').evaluate(i=>i.complete&&i.naturalWidth>0),true);
   for(const label of ['Show visual','Video layout','Explanation']){
    const button=page.getByRole('button',{name:label,exact:true});await button.click();
    const original=await page.locator('#content').innerText();
    await page.getByRole('button',{name:'Ask a question',exact:true}).click();
    assert.equal(await button.isDisabled(),true);
    await page.getByRole('button',{name:'Return to lesson',exact:true}).click();
    assert.equal(await page.locator('#content').innerText(),original);
    assert.equal(await button.getAttribute('aria-pressed'),'true');
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
   }
   await page.screenshot({path:`responsive-qa/presenter-${width}.png`,fullPage:true});
   await page.close();
  }
  console.log('Presenter preview: images, four widths, question interruption and exact layout return PASS');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
