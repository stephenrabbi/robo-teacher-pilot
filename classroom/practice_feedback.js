(() => {
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

  let decorating = false;

  function selectedCopy() {
    return copy[language?.value] || copy.English;
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
    if (decorating) return;
    const isAnswerFeedback = feedback.classList.contains('correct') || feedback.classList.contains('incorrect');
    const raw = feedback.dataset.feedbackRaw || feedback.textContent.trim();
    const hint = ensureNextHint();

    if (!isAnswerFeedback || !raw) {
      delete feedback.dataset.feedbackRaw;
      hint.classList.add('hidden');
      nextButton.classList.remove('practice-next-primary');
      return;
    }

    if (!feedback.dataset.feedbackRaw || feedback.querySelector('.practice-feedback-summary') === null) {
      feedback.dataset.feedbackRaw = raw;
      const parts = raw.split(/\n\s*\n/).map(part => part.trim()).filter(Boolean);
      const message = parts.shift() || raw;
      const explanation = parts.join('\n\n');
      const words = selectedCopy();

      decorating = true;
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
      decorating = false;
    }

    const words = selectedCopy();
    const completed = /view results/i.test(nextButton.textContent || '');
    hint.textContent = completed
      ? words.results
      : (feedback.classList.contains('correct') ? words.correct : words.incorrect);
    hint.classList.remove('hidden');
    nextButton.classList.add('practice-next-primary');
  }

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

  new MutationObserver(decorate).observe(feedback, {
    childList: true,
    characterData: true,
    subtree: true,
    attributes: true,
    attributeFilter: ['class']
  });
  new MutationObserver(decorate).observe(nextButton, {childList: true, characterData: true, subtree: true, attributes: true, attributeFilter: ['class']});
  language?.addEventListener('change', () => {
    delete feedback.dataset.feedbackRaw;
    requestAnimationFrame(decorate);
  });

  decorate();
})();
