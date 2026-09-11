(() => {
  if (document.getElementById('robo-teacher-friendly-error-style')) return;

  const selectors = [
    '.message.teacher',
    '#practiceFeedback',
    '#dailyPlanError',
    '#onboardingError',
    '#understandingFeedback',
    '#revisionFeedback',
    '#teacherVoiceStatus',
    '#learningStatus'
  ];

  function learnerMessage(text) {
    const value = String(text || '').trim();
    if (!value) return null;

    if (/failed to fetch|networkerror|load failed|network request failed|ERR_NETWORK|ERR_INTERNET_DISCONNECTED/i.test(value)) {
      return 'I couldn’t connect. Check your internet and try again.';
    }
    if (/429|too many requests|rate limit|quota|resource exhausted/i.test(value)) {
      return 'Robo-Teacher is busy right now. Please wait a moment, then try again.';
    }
    if (/\b(?:500|502|503|504)\b|internal server error|bad gateway|service unavailable|gateway timeout/i.test(value)) {
      return 'Something went wrong while preparing that. Please try again.';
    }
    if (/timed? out|timeout/i.test(value)) {
      return 'That took too long. Please try again.';
    }
    if (/notallowederror|permission denied|permission.*(?:microphone|camera)|(?:microphone|camera).*permission/i.test(value)) {
      return 'I need permission to use this feature. Allow access in your browser, then try again.';
    }
    if (/\bTypeError\b|\bReferenceError\b|\bSyntaxError\b|\bHTTP\s*\d{3}\b|unexpected token|JSON\.parse/i.test(value)) {
      return 'Something didn’t work as expected. Please try again.';
    }
    return null;
  }

  function decorate(element) {
    if (!(element instanceof Element)) return;
    const text = element.textContent?.trim();
    if (!text) return;
    if (text === element.dataset.friendlyRendered) return;

    const mapped = learnerMessage(text);
    if (!mapped) {
      element.classList.remove('friendly-error-message');
      delete element.dataset.friendlyRendered;
      delete element.dataset.friendlyOriginal;
      return;
    }

    element.dataset.friendlyOriginal = text;
    element.dataset.friendlyRendered = mapped;
    element.textContent = mapped;
    element.classList.add('friendly-error-message');
  }

  function scan(root = document) {
    selectors.forEach(selector => {
      if (root instanceof Element && root.matches(selector)) decorate(root);
      root.querySelectorAll?.(selector).forEach(decorate);
    });
  }

  const style = document.createElement('style');
  style.id = 'robo-teacher-friendly-error-style';
  style.textContent = `
    .friendly-error-message {
      border-radius: 12px;
      line-height: 1.45;
    }
    .message.teacher.friendly-error-message {
      border-left: 4px solid #d39a27;
    }
  `;
  document.head.appendChild(style);

  const observer = new MutationObserver(records => {
    records.forEach(record => {
      if (record.type === 'characterData') {
        decorate(record.target.parentElement);
        return;
      }
      record.addedNodes.forEach(node => {
        if (node.nodeType === Node.ELEMENT_NODE) scan(node);
        else if (node.parentElement) decorate(node.parentElement);
      });
      if (record.target instanceof Element) decorate(record.target);
    });
  });

  observer.observe(document.body, {childList:true, characterData:true, subtree:true});
  scan();
})();
