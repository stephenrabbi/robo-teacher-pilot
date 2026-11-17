// Responsive browser check without real learner records or paid browser automation.
// Runs from repository root against the static classroom shell.
const { chromium, devices } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const output = path.join(process.cwd(), 'responsive-qa');
  fs.mkdirSync(output, { recursive: true });
  let failures = [];
  try {
    for (const width of [375, 768, 1280]) {
      const page = await browser.newPage({ viewport: { width, height: 850 }, deviceScaleFactor: 1 });
      await page.goto('http://127.0.0.1:8765/classroom/index.html', { waitUntil: 'domcontentloaded' });
      // Top navigation must reveal the login panel, not merely scroll to onboarding.
      await page.locator('#newTeacherAccess').click();
      const teacherLoginVisible = await page.locator('#teacherLogin').evaluate(el =>
        !el.classList.contains('hidden') && getComputedStyle(el).display !== 'none' &&
        el.getBoundingClientRect().height > 0);
      assert(teacherLoginVisible, width + 'px: Teacher access did not reveal the login form');
      assert(await page.locator('#teacherAccessKey').isVisible(),
        width + 'px: Teacher access field is not visible');
      await page.evaluate(() => {
        window.scrollTo(0, document.body.scrollHeight);
        window.eval('enterClassroomView()');
      });
      const transition = await page.evaluate(() => ({
        scrollY: window.scrollY,
        landingHidden: getComputedStyle(document.getElementById('welcome')).display === 'none',
        classroomVisible: getComputedStyle(document.getElementById('classroom')).display !== 'none',
        footerHidden: getComputedStyle(document.querySelector('.legal-footer')).display === 'none',
      }));
      console.log('Classroom screen transition:', JSON.stringify(transition));
      assert(transition.landingHidden && transition.classroomVisible && transition.footerHidden,
        'Onboarding did not switch to a dedicated classroom view');
      assert(transition.scrollY <= 2, 'Classroom view did not reset scroll position');
      await page.evaluate(() => document.fonts.ready);
      const result = await page.evaluate(() => {
        const screen = document.querySelector('#classroom');
        const ids = ['teacherPanel', 'question', 'chatForm', 'language', 'canvas', 'readAnswer', 'micButton'];
        const inspected = Object.fromEntries(ids.map(id => {
          const el = document.getElementById(id);
          if (!el) return [id, { missing: true }];
          const rect = el.getBoundingClientRect();
          return [id, { left: Math.round(rect.left), right: Math.round(rect.right),
            width: Math.round(rect.width), visible: rect.width > 0 && rect.height > 0 }];
        }));
        return { viewportWidth: innerWidth, documentWidth: document.documentElement.scrollWidth,
          screenWidth: Math.round(screen.getBoundingClientRect().width), inspected };
      });
      // A consent overlay is outside this isolated classroom-navigation test.
      await page.evaluate(() => { const el=document.getElementById('privacyConsentBanner'); if(el)el.style.display='none'; });
      // Synthetic audio context: exercise the actual read-aloud button handler
      // without a speech API request or an actual audio device.
      if (width === 375) {
        const setup = await page.evaluate(() => {
          try {
            window.eval(`teacherAudioContext = {
              state: 'running',
              suspend: async function () { this.state = 'suspended'; },
              resume: async function () { this.state = 'running'; },
            };
            teacherSpeechPaused = false;
            teacherPanel.classList.add('speaking');
            readAnswerButton.disabled = false;`);
            return true;
          } catch (err) { return String(err); }
        });
        assert.equal(setup, true, 'Could not establish synthetic playback state: ' + setup);
        await page.locator('#readAnswer').click();
        const paused = await page.evaluate(() => ({
          button: document.querySelector('#readAnswer').getAttribute('aria-label'),
          paused: document.querySelector('#teacherPanel').classList.contains('paused'),
        }));
        assert.equal(paused.button, 'Continue reading the answer');
        assert.equal(paused.paused, true);
        await page.locator('#readAnswer').click();
        const resumed = await page.evaluate(() => ({
          button: document.querySelector('#readAnswer').getAttribute('aria-label'),
          speaking: document.querySelector('#teacherPanel').classList.contains('speaking'),
        }));
        assert.equal(resumed.button, 'Pause reading the answer');
        assert.equal(resumed.speaking, true);
        console.log('Synthetic browser pause/resume interaction: PASS');
      }
      await page.screenshot({ path: path.join(output, 'classroom-' + width + '.png'), fullPage: true });
      console.log(JSON.stringify(result));
      if (result.documentWidth > width + 3) failures.push(width + 'px: document overflows by ' + (result.documentWidth - width) + 'px');
      for (const id of ['teacherPanel', 'question', 'chatForm', 'language', 'canvas']) {
        const info = result.inspected[id];
        if (!info || info.missing || !info.visible) failures.push(width + 'px: ' + id + ' is missing/hidden');
        else if (info.left < -4 || info.right > width + 4) failures.push(width + 'px: ' + id + ' exceeds viewport (' + info.left + '..' + info.right + ')');
      }
      await page.close();
    }

    // These are Chromium mobile device emulations, NOT physical phone or
    // Safari/WebKit acceptance tests. No microphones or cloud APIs are used.
    for (const name of ['Pixel 7', 'iPhone 13']) {
      const context = await browser.newContext({
        ...devices[name],
        permissions: [],
      });
      const page = await context.newPage();
      try {
        await page.goto('http://127.0.0.1:8765/classroom/index.html', { waitUntil: 'domcontentloaded' });
        await page.evaluate(() => {
          const banner = document.getElementById('privacyConsentBanner');
          if (banner) banner.style.display = 'none';
          window.eval(`learnerNickname.value='Synthetic Mobile QA';
            learnerCode.value='TEST-MOBILE-QA';
            enterClassroomView();
            lessonChoreography.enabled=false;
            startLessonDirector('Solve x + 5 = 12.',1,
              ['Identify the equation.', 'Subtract 5 from both sides.', 'Check the answer.']);`);
        });
        const label = await page.locator('#lessonStepLabel').innerText();
        assert.equal(label, 'Step 2 of 3', name + ': wrong active lesson step');
        assert.equal(await page.locator('#teacherPanel .teacher-portrait').isVisible(),true,
          name + ': original teacher portrait missing');
        // Touch the actual minimize control, then restore the portrait.
        await page.locator('#toggleTeacher').tap();
        assert.equal(await page.locator('#teacherPanel').evaluate(e=>e.classList.contains('minimized')),true,
          name + ': touch minimize did not work');
        await page.locator('#toggleTeacher').tap();
        assert.equal(await page.locator('#teacherPanel').evaluate(e=>e.classList.contains('minimized')),false,
          name + ': touch restore did not work');
        assert.equal(await page.locator('#lessonStepLabel').innerText(),label,
          name + ': minimizing the teacher changed the lesson');
        const pcm = Buffer.alloc(24000 * 2 * 6);
        for (let i = 0; i < pcm.length / 2; i++) {
          pcm.writeInt16LE(Math.round(6000 * Math.sin(2 * Math.PI * 220 * i / 24000)), i * 2);
        }
        await page.route('**/api/classroom/session', route => route.fulfill({json:{session_token:'synthetic-mobile-audio'}}));
        await page.route('**/api/classroom/speech', route => route.fulfill({
          headers:{'Content-Type':'audio/L16','X-Audio-Sample-Rate':'24000'},body:pcm,
        }));
        const clock = () => page.evaluate(() => window.eval('teacherAudioContext.currentTime'));
        await page.locator('#readAnswer').tap();
        await page.waitForFunction(() => window.eval(
          'teacherStreamComplete && teacherAudioSources.size > 0 && teacherPanel.classList.contains("speaking")'
        ));
        await page.locator('#readAnswer').tap();
        await page.waitForFunction(() => window.eval('teacherSpeechPaused && teacherAudioContext.state === "suspended"'));
        assert.equal(await page.locator('#readAnswer').getAttribute('aria-label'),
          'Continue reading the answer', name + ': pause control incorrect');
        const pausedAt = await clock();
        await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
        assert.equal(await clock(), pausedAt, name + ': audio advanced while paused');
        await page.locator('#readAnswer').tap();
        await page.waitForFunction(position => window.eval('teacherAudioContext.currentTime') > position + .05, pausedAt);
        assert.equal(await page.locator('#readAnswer').getAttribute('aria-label'),
          'Pause reading the answer', name + ': continue control incorrect');
        assert.equal(await page.locator('#lessonStepLabel').innerText(), label,
          name + ': pause/continue changed the lesson step');
        const view = await page.evaluate(() => ({
          width:innerWidth,
          documentWidth:document.documentElement.scrollWidth,
          portraitVisible:!!document.querySelector('#teacherPanel .teacher-portrait')?.getBoundingClientRect().height,
        }));
        assert.ok(view.documentWidth<=view.width+3,
          name+': mobile classroom overflow '+JSON.stringify(view));
        assert.equal(view.portraitVisible,true,name+': teacher portrait hidden after resume');
        console.log(name+': Chromium touch emulation, teacher minimize/restore and pause/continue PASS');
      } finally {
        await context.close();
      }
    }
  } finally { await browser.close(); }
  assert.equal(failures.length, 0, failures.join('; '));
})().catch(err => { console.error(err); process.exitCode = 1; });
