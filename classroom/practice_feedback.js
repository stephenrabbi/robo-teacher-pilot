(() => {
  if (window.__roboTeacherPracticeFeedbackEnhancement) return;
  window.__roboTeacherPracticeFeedbackEnhancement = true;

  const feedback = document.getElementById('practiceFeedback');
  const nextButton = document.getElementById('nextPractice');
  const language = document.getElementById('language');
  if (!feedback || !nextButton) return;

  const copy = {
    English: {
      why: 'WHY THIS ANSWER',
      correct: 'Good work — check the explanation, then continue.',
      incorrect: 'Review why the answer is different, then continue.',
      results: 'Review this feedback, then view your results.'
    },
    Yoruba: {
      why: 'ÌDÍ TÍ ÌDÁHÙN YÌÍ FI RÍ BẸ́Ẹ̀',
      correct: 'Ó dáa — ka àlàyé náà, lẹ́yìn náà tẹ̀síwájú.',
      incorrect: 'Wo ìdí tí ìdáhùn fi yàtọ̀, lẹ́yìn náà tẹ̀síwájú.',
      results: 'Ka àlàyé yìí, lẹ́yìn náà wo èsì rẹ.'
    },
    Igbo: {
      why: 'IHE MERE AZỊZA A JI DỊ OTU A',
      correct: 'Ọ dị mma — gụọ nkọwa ahụ, mesịa gaa n’ihu.',
      incorrect: 'Lee ihe mere azịza ahụ ji dị iche, mesịa gaa n’ihu.',
      results: 'Gụọ nkọwa a, mesịa lee nsonaazụ gị.'
    },
    Hausa: {
      why: 'DALILIN WANNAN AMSAR',
      correct: 'Madalla — karanta bayanin, sannan ka ci gaba.',
      incorrect: 'Duba dalilin da amsar ta bambanta, sannan ka ci gaba.',
      results: 'Karanta wannan bayanin, sannan ka duba sakamakonka.'
    }
  };

  let decorateFrame = 0;

  function selectedCopy() {
    return copy[language?.value] || copy.English;
  }

  function setClass(element, className, enabled) {
    if (element.classList.contains(className) !== enabled) {
      element.classList.toggle(className, enabled);
    }
  }

  function setText(element, text) {
    if (element.textContent !== text) element.textContent = text;
  }

  function ensureNextHint() {
    let hint = document.getElementById('practiceFeedbackNext');
    if (!hint) {
      hint = document.createElement('p');
      hint.id = 'practiceFeedbackNext';
      hint.className = 'practice-feedback-next hidden';
      hint.setAttribute('aria-live', 'polite');
      feedback.after(hint);
    }
    return hint;
  }

  function decorate() {
    decorateFrame = 0;
    const isAnswerFeedback = feedback.classList.contains('correct') || feedback.classList.contains('incorrect');
    const hasDecoratedSummary = feedback.querySelector('.practice-feedback-summary') !== null;
    // When app.js replaces the feedback after a language switch, the old
    // data-feedback-raw value can still exist for one animation frame. If the
    // decorated children have disappeared, trust the newly rendered DOM text
    // and replace the stale cached value instead of repainting the old language.
    const liveText = feedback.textContent.trim();
    const raw = hasDecoratedSummary
      ? (feedback.dataset.feedbackRaw || liveText)
      : liveText;
    const hint = ensureNextHint();

    if (!isAnswerFeedback || !raw) {
      if (feedback.dataset.feedbackRaw) delete feedback.dataset.feedbackRaw;
      setClass(hint, 'hidden', true);
      setClass(nextButton, 'practice-next-primary', false);
      return;
    }

    if (!hasDecoratedSummary) {
      feedback.dataset.feedbackRaw = raw;
      const parts = raw.split(/\n\s*\n/).map(part => part.trim()).filter(Boolean);
      const message = parts.shift() || raw;
      const explanation = parts.join('\n\n');
      const words = selectedCopy();

      feedback.textContent = '';

      const summary = document.createElement('strong');
      summary.className = 'practice-feedback-summary';
      summary.textContent = message;
      feedback.appendChild(summary);

      if (explanation) {
        const label = document.createElement('span');
        label.className = 'practice-feedback-label';
        label.textContent = words.why;
        const detail = document.createElement('span');
        detail.className = 'practice-feedback-detail';
        detail.textContent = explanation;
        feedback.append(label, detail);
      }
    }

    const words = selectedCopy();
    const completed = /view results/i.test(nextButton.textContent || '');
    const hintText = completed
      ? words.results
      : (feedback.classList.contains('correct') ? words.correct : words.incorrect);

    setText(hint, hintText);
    setClass(hint, 'hidden', false);
    setClass(nextButton, 'practice-next-primary', true);
  }

  function scheduleDecorate() {
    if (decorateFrame) return;
    decorateFrame = requestAnimationFrame(decorate);
  }

  if (!document.getElementById('robo-teacher-practice-feedback-style')) {
    const style = document.createElement('style');
    style.id = 'robo-teacher-practice-feedback-style';
    style.textContent = `
      .practice-feedback.correct,
      .practice-feedback.incorrect {
        display: grid;
        gap: 8px;
        padding: 16px 17px;
        border-radius: 14px;
      }
      .practice-feedback-summary {
        display: block;
        font-size: 17px;
        line-height: 1.35;
      }
      .practice-feedback-label {
        display: block;
        margin-top: 2px;
        font-size: 11px;
        font-weight: 850;
        letter-spacing: .7px;
        opacity: .8;
      }
      .practice-feedback-detail {
        display: block;
        white-space: pre-line;
        line-height: 1.55;
      }
      .practice-feedback-next {
        margin: 8px 0 0;
        color: #34445c;
        font-size: 13px;
        font-weight: 700;
        line-height: 1.45;
      }
      #nextPractice.practice-next-primary:not(.hidden) {
        background: #075d45;
        border-color: #075d45;
        color: #fff;
        box-shadow: 0 4px 12px #075d4526;
      }
      #nextPractice.practice-next-primary:not(.hidden):focus-visible {
        outline: 3px solid #67a6ff;
        outline-offset: 2px;
      }
    `;
    document.head.appendChild(style);
  }

  new MutationObserver(scheduleDecorate).observe(feedback, {
    childList: true,
    characterData: true,
    subtree: true,
    attributes: true,
    attributeFilter: ['class']
  });

  // Only text changes matter here. Observing the button's class would react to
  // this enhancement's own class updates and can create an endless mutation loop.
  new MutationObserver(scheduleDecorate).observe(nextButton, {
    childList: true,
    characterData: true,
    subtree: true
  });

  language?.addEventListener('change', () => {
    if (feedback.dataset.feedbackRaw) delete feedback.dataset.feedbackRaw;
    // Leave the old visible feedback alone while the translated response is in
    // flight. app.js will replace it, and that DOM mutation will decorate the
    // new-language feedback. Decorating now would cache and repaint the old
    // language while the request is still pending.
  });

  decorate();
})();
