// Real Chromium, two-page Web Locks smoke tests, synthetic data only.
// Run after bundling browser_lock_adapter.cjs as /bundle.js and starting an HTTP server.
const { test, expect } = require('@playwright/test');
const path=require('node:path');
const fs=require('node:fs');
const http=require('node:http');
let server;
test.beforeAll(async()=>{
 const html='<html><body><script src="/bundle.js"></script></body></html>';
 const script=fs.readFileSync(path.join(__dirname,'../build/synthetic-lock-bundle.js'));
 server=http.createServer((req,res)=>{
  res.setHeader('Cache-Control','no-store');
  if(req.url==='/bundle.js'){res.setHeader('Content-Type','text/javascript');res.end(script)}
  else {res.setHeader('Content-Type','text/html');res.end(html)}
 });
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
});
test.afterAll(async()=>{if(server)await new Promise(resolve=>server.close(resolve))});
test('two real tabs coordinate one synthetic event',async({browser})=>{
 const url='http://127.0.0.1:'+server.address().port;
 const context=await browser.newContext();
 const a=await context.newPage(),b=await context.newPage();
 await a.goto(url);await b.goto(url);
 await a.evaluate(()=>{const api=window.SyntheticBrowserLocks;
  const client=api.createBrowserCrossTabSync({storage:localStorage,scope:{school:'demo',subject:'A'},navigatorObject:navigator});
  client.queue({event_id:'one',correct:2,total:3});
 });
 const start=async page=>page.evaluate(async()=>{const api=window.SyntheticBrowserLocks;
  const client=api.createBrowserCrossTabSync({storage:localStorage,scope:{school:'demo',subject:'A'},navigatorObject:navigator});
  return client.flush(async()=>{const count=Number(localStorage.getItem('upload-count')||0);
    localStorage.setItem('upload-count',String(count+1));await new Promise(r=>setTimeout(r,70));return true});
 });
 await Promise.all([start(a),start(b)]);
 expect(await a.evaluate(()=>Number(localStorage.getItem('upload-count')))).toBe(1);
 expect(await b.evaluate(()=>Object.keys(localStorage).some(k=>k.includes('Queue:v2')))).toBe(true);
 await context.close();
});
test('separate sessions are isolated in real browser storage',async({page})=>{
 await page.goto('http://127.0.0.1:'+server.address().port);
 const counts=await page.evaluate(()=>{
 const api=window.SyntheticBrowserLocks;
 const c1=api.createBrowserCrossTabSync({storage:localStorage,scope:{school:'demo',subject:'A'},navigatorObject:navigator});
 const c2=api.createBrowserCrossTabSync({storage:localStorage,scope:{school:'demo',subject:'B'},navigatorObject:navigator});
 c1.queue({event_id:'a'});return [c1.pending(),c2.pending()];
 });expect(counts).toEqual([1,0]);
});
