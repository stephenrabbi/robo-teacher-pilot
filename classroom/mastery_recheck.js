(() => {
  if (typeof understandingForm === 'undefined' || !understandingForm) return;

  let masteryRetryActive = false;

  const copy = {
    English: {
      correct: 'Correct!',
      mastered: 'Mastery confirmed.',
      masteredStatus: 'Mastery confirmed',
      retryPreparing: 'Reteaching, then preparing one more check',
      retryReady: 'Read the simpler explanation, then try the new check',
      retryButton: 'Check again',
      preparingButton: 'Preparing another check…',
      needsReview: 'This topic still needs review.',
      needsReviewStatus: 'This topic still needs review',
      checked: 'Checked',
      checking: 'Checking…',
      checkAnswer: 'Check my answer',
      retryFailed: 'I could not prepare the follow-up check right now. You can return to the lesson and try again.'
    },
    Yoruba: {
      correct: 'Ó tọ́!',
      mastered: 'O ti lóye rẹ̀.',
      masteredStatus: 'O ti lóye rẹ̀',
      retryPreparing: 'A ń ṣàlàyé rẹ̀ lọ́nà míì, a ó sì tún ṣàyẹ̀wò rẹ',
      retryReady: 'Ka àlàyé tó rọrùn yìí, lẹ́yìn náà dá ìbéèrè tuntun náà',
      retryButton: 'Ṣàyẹ̀wò lẹ́ẹ̀kan síi',
      preparingButton: 'A ń pèsè ìbéèrè míì…',
      needsReview: 'A tún nílò àtúnyẹ̀wò lórí kókó yìí.',
      needsReviewStatus: 'Kókó yìí tún nílò àtúnyẹ̀wò',
      checked: 'A ti ṣàyẹ̀wò',
      checking: 'A ń ṣàyẹ̀wò…',
      checkAnswer: 'Ṣàyẹ̀wò ìdáhùn mi',
      retryFailed: 'Mi ò lè pèsè ìbéèrè míì báyìí. Padà sí ẹ̀kọ́ náà kí o sì tún gbìyànjú.'
    },
    Igbo: {
      correct: 'Ọ dị mma!',
      mastered: 'Ị ghọtala ya.',
      masteredStatus: 'Ị ghọtala ya',
      retryPreparing: 'A na-akọwa ya n’ụzọ ọzọ ma na-akwadebe ajụjụ ọzọ',
      retryReady: 'Gụọ nkọwa dị mfe, wee zaa ajụjụ ọhụrụ ahụ',
      retryButton: 'Lelee ọzọ',
      preparingButton: 'Na-akwadebe ajụjụ ọzọ…',
      needsReview: 'Isiokwu a ka chọrọ ntụle ọzọ.',
      needsReviewStatus: 'Isiokwu a ka chọrọ ntụle ọzọ',
      checked: 'Enyochala',
      checking: 'Na-enyocha…',
      checkAnswer: 'Lelee azịza m',
      retryFailed: 'Enweghị m ike ịkwadebe ajụjụ ọzọ ugbu a. Laghachi n’ihe ọmụmụ ma nwaa ọzọ.'
    },
    Hausa: {
      correct: 'Daidai!',
      mastered: 'Ka fahimta.',
      masteredStatus: 'Ka fahimta',
      retryPreparing: 'Ana sake bayani ta wata hanya sannan a shirya tambaya guda ɗaya',
      retryReady: 'Karanta bayanin mai sauƙi, sannan ka amsa sabuwar tambayar',
      retryButton: 'Sake dubawa',
      preparingButton: 'Ana shirya wata tambaya…',
      needsReview: 'Har yanzu ana bukatar sake duba wannan batu.',
      needsReviewStatus: 'Har yanzu wannan batu yana bukatar sake dubawa',
      checked: 'An duba',
      checking: 'Ana dubawa…',
      checkAnswer: 'Duba amsata',
      retryFailed: 'Ba zan iya shirya sabuwar tambaya yanzu ba. Koma darasin ka sake gwadawa.'
    }
  };

  function currentCopy() {
    return copy[language?.value] || copy.English;
  }

  function resetMasteryRetry() {
    masteryRetryActive = false;
  }

  function renderRetryCheck(data) {
    understandingCheckId = data.check_id;
    understandingQuestion.textContent = data.question;
    understandingChoices.replaceChildren();
    data.choices.forEach((choice, index) => {
      const label = document.createElement('label');
      const input = document.createElement('input');
      const span = document.createElement('span');
      input.type = 'radio';
      input.name = 'understandingChoice';
      input.value = String(index);
      input.required = true;
      span.textContent = choice;
      label.append(input, span);
      understandingChoices.appendChild(label);
    });
  }

  async function prepareMasteryRetry(reteachText) {
    const token = await ensureSession();
    const response = await fetch('/api/classroom/understanding/start', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        text: reteachText,
        session_token: token,
        language: language.value
      })
    });
    const data = await response.json();
    if (response.status === 401) sessionToken = null;
    if (!response.ok) throw new Error(data.detail || 'follow-up check');
    return data;
  }

  understandingButton?.addEventListener('click', resetMasteryRetry, true);
  closeUnderstandingButton?.addEventListener('click', resetMasteryRetry, true);

  if (typeof startUnderstandingCheck === 'function') {
    const baseStartUnderstandingCheck = startUnderstandingCheck;
    startUnderstandingCheck = async function (...args) {
      resetMasteryRetry();
      return baseStartUnderstandingCheck(...args);
    };
  }

  understandingForm.addEventListener('submit', async event => {
    event.preventDefault();
    event.stopImmediatePropagation();

    const selected = understandingForm.querySelector('input[name="understandingChoice"]:checked');
    if (!selected || !understandingCheckId) return;

    const text = currentCopy();
    const submitButton = understandingForm.querySelector('button[type="submit"]');
    const wasRetry = masteryRetryActive;
    const answeredCheckId = understandingCheckId;
    const questionText = understandingQuestion.textContent || '';
    const choiceLabels = Array.from(understandingChoices.querySelectorAll('label span')).map(item => item.textContent || '');
    const selectedText = choiceLabels[Number(selected.value)] || '';
    submitButton.disabled = true;
    submitButton.textContent = text.checking;

    try {
      const token = await ensureSession();
      const response = await fetch('/api/classroom/understanding/answer', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          session_token: token,
          check_id: answeredCheckId,
          choice_index: Number(selected.value)
        })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'answer');

      recordLearningSignal(data.correct ? 'correct' : 'incorrect');
      const correctText = choiceLabels[Number(data.correct_index)] || '';
      if (typeof window.roboTeacherMasteryRecord === 'function') {
        void window.roboTeacherMasteryRecord({
          correct: data.correct,
          stage: wasRetry ? 'reteach' : 'initial',
          checkId: answeredCheckId,
          question: data.correct ? '' : questionText,
          selectedChoice: data.correct ? '' : selectedText,
          correctChoice: data.correct ? '' : correctText,
          feedback: data.correct ? '' : (data.feedback || '')
        });
      }
      understandingChoices.querySelectorAll('label').forEach((label, index) => {
        label.classList.toggle('correct-choice', index === data.correct_index);
        label.querySelector('input').disabled = true;
      });

      if (data.correct) {
        understandingFeedback.textContent = `${wasRetry ? text.mastered : text.correct} ${data.feedback}`;
        understandingFeedback.className = 'practice-feedback correct';
        setLearningStatus(wasRetry ? text.masteredStatus : 'You understood it', 'success');
        submitButton.textContent = wasRetry ? text.masteredStatus : text.correct.replace('!', '');
        resetMasteryRetry();
        return;
      }

      understandingFeedback.textContent = `Not quite. ${data.feedback}`;
      understandingFeedback.className = 'practice-feedback incorrect';

      if (wasRetry) {
        setLearningStatus(text.needsReviewStatus, 'attention');
        understandingFeedback.textContent = `${text.needsReview} ${data.feedback}`;
        submitButton.textContent = text.checked;
        resetMasteryRetry();
        return;
      }

      setLearningStatus(text.retryPreparing, 'thinking');
      submitButton.textContent = text.preparingButton;
      const retry = await prepareMasteryRetry(data.feedback);
      renderRetryCheck(retry);
      masteryRetryActive = true;
      submitButton.disabled = false;
      submitButton.textContent = text.retryButton;
      setLearningStatus(text.retryReady, 'attention');
    } catch (error) {
      understandingFeedback.textContent = masteryRetryActive ? text.retryFailed : (error.message || 'I could not check that answer. Please try again.');
      understandingFeedback.className = 'practice-feedback incorrect';
      submitButton.disabled = false;
      submitButton.textContent = masteryRetryActive ? text.retryButton : text.checkAnswer;
      setLearningStatus('Understanding check needs another try', 'attention');
    }
  }, true);
})();
