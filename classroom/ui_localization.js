(() => {
  const language = document.getElementById('language');
  if (!language || document.getElementById('roboTeacherUiLocalizationStyle')) return;

  const copy = {
    English: {
      home: 'Home', more: 'More', homeAria: 'Open learning home', moreAria: 'More classroom tools',
      support: 'Need another way to learn this?', addTools: 'Add image or use whiteboard',
      onboarding: 'Choose your nickname and class, then start learning.',
      dataSaver: 'Data Saver', on: 'On', off: 'Off',
      saverOn: 'Data Saver is on. Visuals and media will ask before loading.',
      saverOff: 'Data Saver is off. Visuals and media will load normally.',
      saverLoad: 'Data Saver is on. Tap again to load this once.',
      states: {ready:'Ready', listening:'Listening', thinking:'Thinking', teaching:'Teaching', paused:'Paused', retry:'Retry'}
    },
    Yoruba: {
      home: 'Ilé', more: 'Síi', homeAria: 'Ṣí ojú ilé ẹ̀kọ́', moreAria: 'Àwọn irinṣẹ́ míì',
      support: 'Ṣé o fẹ́ kí n ṣàlàyé rẹ̀ ní ọ̀nà míì?', addTools: 'Fi àwòrán kun tàbí lo whiteboard',
      onboarding: 'Yan orúkọ tí a máa pè ọ́ àti kíláàsì rẹ, lẹ́yìn náà bẹ̀rẹ̀ ẹ̀kọ́.',
      dataSaver: 'Data Saver', on: 'Tan', off: 'Pa',
      saverOn: 'Data Saver ti tan. Àwòrán àti media yóò béèrè kí o tó ṣí wọn.',
      saverOff: 'Data Saver ti pa. Àwòrán àti media yóò ṣí bíi ti tẹ́lẹ̀.',
      saverLoad: 'Data Saver ti tan. Tẹ lẹ́ẹ̀kan síi láti ṣí èyí.',
      states: {ready:'Ṣetan', listening:'Ń gbọ́', thinking:'Ń ronú', teaching:'Ń kọ́ni', paused:'Dúró', retry:'Gbìyànjú lẹ́ẹ̀kansi'}
    },
    Igbo: {
      home: 'Ụlọ', more: 'Ọzọ', homeAria: 'Mepee ụlọ mmụta', moreAria: 'Ngwa ndị ọzọ',
      support: 'Ị chọrọ ka a kọwaa ya n’ụzọ ọzọ?', addTools: 'Tinye onyonyo ma ọ bụ jiri whiteboard',
      onboarding: 'Họrọ aha a ga-akpọ gị na klas gị, wee malite ịmụ ihe.',
      dataSaver: 'Data Saver', on: 'Gbanye', off: 'Gbanyụọ',
      saverOn: 'Data Saver agbanyela. Onyonyo na media ga-ajụ tupu ha ebido.',
      saverOff: 'Data Saver agbanyụrụ. Onyonyo na media ga-ebido dịka ọ dị na mbụ.',
      saverLoad: 'Data Saver agbanyela. Pịa ọzọ ka i mepee nke a otu ugboro.',
      states: {ready:'Njikere', listening:'Na-ege ntị', thinking:'Na-eche', teaching:'Na-akụzi', paused:'Kwụsịrị', retry:'Gbalịa ọzọ'}
    },
    Hausa: {
      home: 'Gida', more: 'Ƙari', homeAria: 'Buɗe shafin gida na koyo', moreAria: 'Ƙarin kayan aji',
      support: 'Kana son a bayyana wannan ta wata hanya?', addTools: 'Ƙara hoto ko amfani da whiteboard',
      onboarding: 'Zaɓi sunan da za a kira ka da ajinka, sannan ka fara koyo.',
      dataSaver: 'Data Saver', on: 'Kunna', off: 'Kashe',
      saverOn: 'Data Saver yana kunne. Hotuna da media za su tambaya kafin su buɗe.',
      saverOff: 'Data Saver a kashe yake. Hotuna da media za su buɗe kamar yadda aka saba.',
      saverLoad: 'Data Saver yana kunne. Danna kuma sau ɗaya don buɗe wannan.',
      states: {ready:'A shirye', listening:'Ina sauraro', thinking:'Ina tunani', teaching:'Ina koyarwa', paused:'An dakata', retry:'Sake gwadawa'}
    }
  };

  function words() { return copy[language.value] || copy.English; }

  function apply() {
    const t = words();
    const home = document.getElementById('learnerHomeButton');
    if (home) { home.textContent = t.home; home.setAttribute('aria-label', t.homeAria); }

    const more = document.querySelector('.class-tools-more > summary');
    if (more) { more.textContent = t.more; more.setAttribute('aria-label', t.moreAria); }

    const support = document.querySelector('.contextual-lesson-actions-label');
    if (support) support.textContent = t.support;

    const add = document.querySelector('.input-tools-more > summary');
    if (add) { add.setAttribute('aria-label', t.addTools); add.setAttribute('title', t.addTools); }

    const onboarding = document.getElementById('onboardingPrimaryHint');
    if (onboarding) onboarding.textContent = t.onboarding;

    const saver = document.getElementById('dataSaverButton');
    if (saver) {
      const enabled = saver.getAttribute('aria-pressed') === 'true';
      saver.textContent = `${t.dataSaver}: ${enabled ? t.on : t.off}`;
      saver.setAttribute('aria-label', `${t.dataSaver}: ${enabled ? t.on : t.off}`);
    }

    const pill = document.getElementById('learningStatePill');
    if (pill) {
      const state = pill.dataset.state || 'ready';
      pill.textContent = t.states[state] || t.states.ready;
    }

    const notice = document.getElementById('dataSaverNotice');
    if (notice && notice.textContent.trim()) {
      const text = notice.textContent.trim();
      let next = text;
      if (/Data Saver is on\. Visuals and media/i.test(text) || /Data Saver ti tan\. Àwòrán/i.test(text) || /Data Saver agbanyela\. Onyonyo/i.test(text) || /Data Saver yana kunne\. Hotuna/i.test(text)) next = t.saverOn;
      else if (/Data Saver is off/i.test(text) || /Data Saver ti pa/i.test(text) || /Data Saver agbanyụrụ/i.test(text) || /Data Saver a kashe yake/i.test(text)) next = t.saverOff;
      else if (/Data Saver is on\. Tap/i.test(text) || /Tẹ lẹ́ẹ̀kan síi/i.test(text) || /Pịa ọzọ/i.test(text) || /Danna kuma/i.test(text)) next = t.saverLoad;
      if (next !== text) notice.textContent = next;
    }
  }

  language.addEventListener('change', () => requestAnimationFrame(apply));

  const observer = new MutationObserver(() => requestAnimationFrame(apply));
  observer.observe(document.body, {childList:true, subtree:true, attributes:true, attributeFilter:['data-state','aria-pressed']});

  const style = document.createElement('style');
  style.id = 'roboTeacherUiLocalizationStyle';
  style.textContent = `.class-tools.nav-redesigned > button, .class-tools.nav-redesigned > .class-tools-more > summary { overflow-wrap:anywhere; }`;
  document.head.appendChild(style);

  apply();
})();
