(() => {
  const CONSENT_KEY = 'roboTeacherPrivacyConsentV1';
  const EXTERNAL_KEY = 'roboTeacherExternalContentV1';

  function getChoice(key) {
    try { return localStorage.getItem(key); } catch (_) { return null; }
  }
  function setChoice(key, value) {
    try { localStorage.setItem(key, value); } catch (_) {}
  }
  function externalContentAllowed() { return getChoice(EXTERNAL_KEY) === 'allow'; }

  function showExternalPlaceholder(url, title) {
    const frame = document.getElementById('mediaFrame');
    const replay = document.getElementById('mediaReplay');
    const source = document.getElementById('mediaSource');
    if (!frame || !replay) return;
    frame.classList.add('hidden');
    frame.removeAttribute('src');
    replay.classList.remove('hidden');
    replay.replaceChildren();
    const box = document.createElement('div');
    box.className = 'external-content-consent';
    const heading = document.createElement('strong');
    heading.textContent = title || 'External learning content';
    const text = document.createElement('p');
    text.textContent = 'This simulation is provided by a third party (for example PhET). Loading it may allow that provider to receive technical data and use cookies or similar storage. It will not load until you allow optional external content.';
    const allow = document.createElement('button');
    allow.type = 'button';
    allow.textContent = 'Allow and open simulation';
    allow.addEventListener('click', () => {
      setChoice(EXTERNAL_KEY, 'allow');
      replay.classList.add('hidden');
      frame.src = url;
      frame.classList.remove('hidden');
      updateBannerState();
    });
    box.append(heading, text, allow);
    replay.appendChild(box);
    if (source) source.textContent = 'External content blocked until you choose to allow it.';
  }

  window.RoboTeacherPrivacy = {
    externalContentAllowed,
    requestExternalContent: showExternalPlaceholder,
  };

  function clearOnboarding() {
    ['learnerNickname','learnerCode'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = '';
    });
    const consent = document.getElementById('learnerConsent');
    if (consent) consent.checked = false;
    document.getElementById('learnerNickname')?.focus();
  }

  function clearDeviceData() {
    if (!confirm('Clear Robo-Teacher data saved in this browser on this device? This removes local preferences, saved lessons, local learner names and continuity data. It does not automatically delete server-side pilot records.')) return;
    try {
      Object.keys(localStorage).filter(k => k.startsWith('roboTeacher')).forEach(k => localStorage.removeItem(k));
      Object.keys(sessionStorage).filter(k => k.startsWith('roboTeacher')).forEach(k => sessionStorage.removeItem(k));
    } catch (_) {}
    location.reload();
  }

  function buildBanner() {
    if (document.getElementById('privacyConsentBanner')) return;
    const banner = document.createElement('aside');
    banner.id = 'privacyConsentBanner';
    banner.className = 'privacy-consent-banner';
    banner.setAttribute('aria-label','Privacy and cookie choices');
    banner.innerHTML = `
      <div>
        <strong>Privacy & cookie choices</strong>
        <p>Robo-Teacher does not currently use advertising or behavioural analytics cookies. Essential browser storage is used for learning continuity. Optional third-party learning content may use cookies or similar storage and stays blocked unless you allow it.</p>
        <a href="/classroom/cookie-policy.html">Read Cookie Policy</a>
      </div>
      <div class="privacy-consent-actions">
        <button type="button" data-choice="essential">Essential only</button>
        <button type="button" data-choice="allow" class="primary-consent">Allow external content</button>
        <button type="button" data-action="clear-device">Clear this device data</button>
      </div>`;
    document.body.appendChild(banner);
    banner.querySelector('[data-choice="essential"]').addEventListener('click', () => {
      setChoice(EXTERNAL_KEY, 'essential');
      banner.classList.add('hidden');
    });
    banner.querySelector('[data-choice="allow"]').addEventListener('click', () => {
      setChoice(EXTERNAL_KEY, 'allow');
      banner.classList.add('hidden');
    });
    banner.querySelector('[data-action="clear-device"]').addEventListener('click', clearDeviceData);
    if (getChoice(EXTERNAL_KEY)) banner.classList.add('hidden');
  }

  function updateBannerState() {
    const banner = document.getElementById('privacyConsentBanner');
    if (banner && getChoice(EXTERNAL_KEY)) banner.classList.add('hidden');
  }

  function wireConsent() {
    const start = document.getElementById('startLearning');
    const consent = document.getElementById('learnerConsent');
    const error = document.getElementById('onboardingError');
    if (start && consent) {
      start.addEventListener('click', event => {
        if (!consent.checked) {
          event.preventDefault();
          event.stopImmediatePropagation();
          if (error) {
            error.textContent = 'Please confirm the privacy and permission statement before starting.';
            error.classList.remove('hidden');
          }
          consent.focus();
          return;
        }
        setChoice(CONSENT_KEY, JSON.stringify({version:1, acceptedAt:new Date().toISOString()}));
      }, true);
      if (getChoice(CONSENT_KEY)) consent.checked = true;
    }

    document.getElementById('clearOnboarding')?.addEventListener('click', clearOnboarding);
    document.getElementById('clearQuestion')?.addEventListener('click', () => {
      const q = document.getElementById('question'); if (q) { q.value=''; q.focus(); }
    });
    document.getElementById('clearPracticeAnswer')?.addEventListener('click', () => {
      const a = document.getElementById('practiceAnswer'); if (a) { a.value=''; a.focus(); }
    });
    document.getElementById('privacyChoices')?.addEventListener('click', () => {
      const banner = document.getElementById('privacyConsentBanner');
      if (banner) banner.classList.remove('hidden');
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    buildBanner();
    wireConsent();
  });
})();