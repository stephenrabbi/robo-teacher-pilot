const assert = require('node:assert/strict');
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  try {
    for (const viewport of [{width: 1280, height: 800}, {width: 390, height: 844}]) {
      const page = await browser.newPage({viewport});
      try {
        await page.goto('https://robo-teacher-maths-classroom-qa.onrender.com/classroom-app', {
          waitUntil: 'domcontentloaded', timeout: 90000
        });
        await page.evaluate(() => {
          learnerNickname.value = 'Hosted Maths QA';
          learnerClass.value = 'JSS2';
          enterClassroomView();
          document.getElementById('privacyConsentBanner')?.classList.add('hidden');
        });
        await page.getByRole('button', {name: 'Try a simple equation'}).click();
        await page.locator('#nextLessonStep').click();
        assert.equal(await page.locator('#canvasAnswer').innerText(), 'Add two to both sides of the equation.');
        const speechResponse = page.waitForResponse(response =>
          response.url().endsWith('/api/classroom/speech') && response.request().method() === 'POST'
        );
        await page.locator('#readAnswer').click();
        const response = await speechResponse;
        assert.equal(response.status(), 200);
        assert.equal(JSON.parse(response.headers()['x-robo-mouth-cues']).length, 16);
        await page.waitForFunction(() => {
          const cue = document.getElementById('teacherPanel').dataset.mouthCue;
          return cue && cue !== 'X';
        });
        assert.equal((await response.body()).length, 186240);
        const audioClock = () => page.evaluate(() => teacherAudioContext.currentTime);
        await page.locator('#readAnswer').click();
        await page.waitForFunction(() => teacherSpeechPaused && teacherAudioContext.state === 'suspended');
        assert.equal(await page.locator('#teacherPanel').getAttribute('data-mouth-cue'), null);
        const pausedAt = await audioClock();
        await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
        assert.equal(await audioClock(), pausedAt);

        await page.locator('#readAnswer').click();
        await page.waitForFunction(position => teacherAudioContext.currentTime > position + 0.05, pausedAt);
        await page.waitForFunction(() => Boolean(document.getElementById('teacherPanel').dataset.mouthCue));
        console.log(`Hosted prepared narration and avatar passed at ${viewport.width}px`);
      } finally {
        await page.close();
      }
    }
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
