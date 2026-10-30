// Test real app PCM stream decoder using locally generated synthetic audio.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required']});
  try {
    const page = await browser.newPage();
    await page.goto('http://127.0.0.1:8765/classroom/index.html',{waitUntil:'domcontentloaded'});
    const result = await page.evaluate(async () => {
      const bytes=new Uint8Array(24000*2), view=new DataView(bytes.buffer);
      for(let i=0;i<24000;i++)view.setInt16(i*2,Math.round(900*Math.sin(2*Math.PI*220*i/24000)),true);
      window.__syntheticPcmChunks=[bytes.slice(0,1001),bytes.slice(1001,21007),bytes.slice(21007)];
      return await window.eval(`(async()=>{
        teacherSpeechRequest+=1;
        teacherStreamComplete=false;
        teacherSpeechPaused=false;
        await prepareTeacherAudio();
        const id=teacherSpeechRequest;
        const response=new Response(new ReadableStream({
          start(controller){
            for(const chunk of window.__syntheticPcmChunks)controller.enqueue(chunk);
            controller.close();
          }
        }));
        await playPcmStream(response,id);
        return {sampleRate:teacherAudioContext.sampleRate,
          completed:teacherStreamComplete,
          activeAudioSources:teacherAudioSources.size};
      })()`);
    });
    console.log('Robo-Teacher PCM stream:',JSON.stringify(result));
    assert.equal(result.sampleRate,24000);
    assert.equal(result.completed,true);
    console.log('App PCM stream browser test: PASS');
  } finally { await browser.close(); }
})().catch(err=>{console.error(err);process.exitCode=1});
