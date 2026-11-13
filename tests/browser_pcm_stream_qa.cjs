// Test real app PCM stream decoder using locally generated synthetic audio.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required']});
  try {
    const page = await browser.newPage();
    await page.goto('http://127.0.0.1:8765/classroom/index.html',{waitUntil:'domcontentloaded'});
    await page.locator('#classroom').evaluate(el => { document.querySelector('#welcome')?.classList.add('hidden'); el.classList.remove('hidden'); });
    await page.evaluate(() => {const el=document.getElementById('privacyConsentBanner'); if(el)el.style.display='none';});
    const result = await page.evaluate(async () => {
      const bytes=new Uint8Array(24000*8), view=new DataView(bytes.buffer);
      for(let i=0;i<24000*4;i++){
        if(i>=24000*1.4&&i<24000*2.4)continue;
        view.setInt16(i*2,Math.round(7000*Math.sin(2*Math.PI*220*i/24000)),true);
      }
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
    const mouth=()=>page.locator('#teacherPanel').evaluate(el=>Number(el.style.getPropertyValue('--mouth-open')));
    await page.waitForFunction(()=>Number(document.getElementById('teacherPanel').style.getPropertyValue('--mouth-open'))>.15);
    const speakingOverlay = page.locator('#teacherPanel .avatar-head-speaking');
    await page.emulateMedia({reducedMotion:'reduce'});
    assert.equal(await speakingOverlay.evaluate(el => getComputedStyle(el).opacity), '0');
    await page.emulateMedia({reducedMotion:'no-preference'});
    // Test the real app's Read Answer handler against the actual Web Audio context.
    await page.locator('#readAnswer').click();
    const paused = await page.evaluate(() => window.eval(`({
      paused: teacherSpeechPaused,
      state: teacherAudioContext.state,
      label: readAnswerButton.getAttribute('aria-label'),
      currentTime: teacherAudioContext.currentTime
    })`));
    assert.equal(paused.paused, true);
    assert.equal(paused.state, 'suspended');
    assert.equal(paused.label, 'Continue reading the answer');
    assert.equal(await mouth(),0);
    await page.waitForTimeout(150);
    const whilePaused = await page.evaluate(() => window.eval('teacherAudioContext.currentTime'));
    assert(Math.abs(whilePaused - paused.currentTime) < 0.01, 'Audio advanced while paused');
    await page.locator('#readAnswer').click();
    await page.waitForFunction(() => window.eval('teacherSpeechPaused === false'), {timeout:3000});
    const resumed = await page.evaluate(() => window.eval(`({
      paused: teacherSpeechPaused,
      state: teacherAudioContext.state,
      label: readAnswerButton.getAttribute('aria-label')
    })`));
    assert.equal(resumed.paused, false);
    assert.equal(resumed.state, 'running');
    assert.equal(resumed.label, 'Pause reading the answer');
    await page.waitForFunction(()=>Number(document.getElementById('teacherPanel').style.getPropertyValue('--mouth-open'))>.15);
    await page.waitForFunction(()=>window.eval('teacherAudioContext.currentTime>1.85'));
    assert.equal(await mouth(),0,'The Maths avatar should close its mouth during silence');
    await page.waitForFunction(()=>Number(document.getElementById('teacherPanel').style.getPropertyValue('--mouth-open'))>.15);
    console.log('App PCM stream Read Answer Pause/Continue and avatar motion on real Web Audio: PASS');
    // Exercise the classroom question and resume handlers with real Web Audio
    // and deterministic responses. The recognition transcript is synthetic.
    const originalStep='Add two to both sides of the equation.';
    const followUp='Adding the same number keeps both sides equal.';
    const speechRequests=[];
    const originalAudio = Buffer.alloc(24000 * 2 * 4);
    for (let sample = 0; sample < originalAudio.length / 2; sample++) {
      originalAudio.writeInt16LE(Math.round(7000 * Math.sin(2 * Math.PI * 220 * sample / 24000)), sample * 2);
    }
    await page.route('**/*',route=>{
      const url=new URL(route.request().url());
      if(url.origin!=='http://127.0.0.1:8765')return route.abort();
      if(url.pathname==='/')return route.fulfill({json:{status:'ready'}});
      if(url.pathname==='/api/classroom/session')return route.fulfill({json:{session_token:'synthetic-narration-session'}});
      if(url.pathname==='/api/classroom/chat')return route.fulfill({json:{reply:followUp}});
      if(url.pathname==='/api/classroom/speech'){
        const {text}=route.request().postDataJSON();
        speechRequests.push(text);
        return route.fulfill({contentType:'audio/L16',body:text===originalStep?originalAudio:Buffer.alloc(24000)});
      }
      return route.continue();
    });
    await page.evaluate(step=>window.eval(`(()=>{
      stopTeacherAudio();
      learnerNickname.value='Synthetic Narration QA';
      learnerCode.value='TEST-NARRATION-QA';
      enterClassroomView();
      showCanvasAnswer(${JSON.stringify(step)});
      handsFree.enabled=true;
    })()`),originalStep);
    await page.locator('#readAnswer').click();
    await page.waitForFunction(()=>window.eval(
      'teacherStreamComplete && activeMathsNarration && teacherAudioContext.currentTime-activeMathsNarration.chunks[0].start>.2'
    ));
    const mouthIsMoving = () => Number(document.getElementById('teacherPanel').style.getPropertyValue('--mouth-open')) > .15;
    await page.waitForFunction(mouthIsMoving);
    await page.evaluate(()=>window.eval(`handsFreeBargeIn([{transcript:'Robo-Teacher, why do we add to both sides?'}])`));
    await page.waitForFunction(()=>window.eval('teacherSpeechPaused && teacherAudioContext.state==="suspended"'));
    assert.equal(await mouth(), 0, 'Interrupting narration should close the avatar mouth');
    await page.evaluate(()=>window.eval(`handleHandsFreePhrase('Robo-Teacher, why do we add to both sides?',.99)`));
    await page.waitForFunction(()=>window.eval('Boolean(handsFree.resumeOffer)'));
    const offset=await page.evaluate(()=>window.eval(
      'mathsNarrationCheckpoints.get(handsFree.resumeOffer.interruptedLesson).chunks[0].offset'
    ));
    assert.ok(offset>.2&&offset<4,'Expected an interruption inside the original narration');
    await page.evaluate(()=>window.eval("handleHandsFreePhrase('Continue',.99)"));
    await page.waitForFunction(()=>window.eval(
      'activeMathsNarration?.chunks[0]?.offset>0 && teacherPanel.classList.contains("speaking")'
    ));
    assert.equal(await page.evaluate(()=>window.eval('activeMathsNarration.chunks[0].offset')),offset);
    assert.equal(await page.locator('#canvasAnswer').innerText(),originalStep);
    await page.waitForFunction(mouthIsMoving);
    assert.deepEqual(speechRequests,[originalStep,followUp]);
    console.log('Maths narration resumed at the saved audio offset without another speech request: PASS');
    console.log('App PCM stream browser test: PASS');
  } finally { await browser.close(); }
})().catch(err=>{console.error(err);process.exitCode=1});
