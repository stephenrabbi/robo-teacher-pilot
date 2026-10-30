// Real Web Audio API engine smoke test using a locally generated oscillator.
// No learner session, speech provider call, or paid API.
// This does NOT verify the remote voice model or audible output from physical speakers.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--autoplay-policy=no-user-gesture-required'] });
  try {
    const page = await browser.newPage();
    await page.goto('http://127.0.0.1:8765/classroom/index.html', { waitUntil: 'domcontentloaded' });
    const observation = await page.evaluate(async () => {
      const Context = window.AudioContext || window.webkitAudioContext;
      if (!Context) throw new Error('Web Audio is unavailable');
      const context = new Context({ sampleRate: 24000 });
      const oscillator = context.createOscillator();
      const gain = context.createGain();
      gain.gain.value = 0; // Silence speaker output while audio render timing progresses.
      oscillator.connect(gain).connect(context.destination);
      oscillator.start();
      try {
        await context.resume();
        await new Promise(resolve => setTimeout(resolve, 150));
        const beforePause = context.currentTime;
        await context.suspend();
        const pausedAt = context.currentTime;
        await new Promise(resolve => setTimeout(resolve, 150));
        const whilePaused = context.currentTime;
        await context.resume();
        await new Promise(resolve => setTimeout(resolve, 150));
        const afterResume = context.currentTime;
        return {
          sampleRate: context.sampleRate,
          beforePause, pausedAt, whilePaused, afterResume,
          pauseDelta: whilePaused - pausedAt, resumeDelta: afterResume - whilePaused,
        };
      } finally {
        oscillator.stop();
        await context.close();
      }
    });
    console.log('Web Audio real-engine observation:', JSON.stringify(observation));
    assert.equal(observation.sampleRate, 24000);
    assert(observation.beforePause > 0, 'Audio timeline never started');
    assert(observation.pauseDelta < 0.01, 'Audio timeline advanced while suspended');
    assert(observation.resumeDelta > 0.05, 'Audio timeline did not advance after resume');
    console.log('Web Audio real-engine suspend/resume: PASS');
  } finally {
    await browser.close();
  }
})().catch(err => { console.error(err); process.exitCode = 1; });
