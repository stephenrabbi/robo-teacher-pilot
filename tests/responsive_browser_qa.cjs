// Responsive browser check without real learner records or paid browser automation.
// Runs from repository root against the static classroom shell.
const { chromium } = require('playwright');
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
      await page.locator('#classroom').evaluate(el => {
        document.querySelector('#welcome')?.classList.add('hidden');
        el.classList.remove('hidden');
      });
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
            teacherPanel.classList.add('speaking');`);
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
  } finally { await browser.close(); }
  assert.equal(failures.length, 0, failures.join('; '));
})().catch(err => { console.error(err); process.exitCode = 1; });
