(() => {
  if (window.__roboTeacherPracticeReliability) return;
  window.__roboTeacherPracticeReliability = true;

  const nativeFetch = window.fetch.bind(window);
  const language = document.getElementById('language');
  const PRACTICE_PATH = '/api/classroom/practice/';
  const RECOVERABLE_ACTIONS = new Set(['answer', 'next']);

  function practiceAction(input) {
    const url = typeof input === 'string' ? input : input?.url;
    if (!url || !url.includes(PRACTICE_PATH)) return null;
    const action = url.split(PRACTICE_PATH, 2)[1]?.split(/[?#]/, 1)[0];
    return RECOVERABLE_ACTIONS.has(action) ? action : null;
  }

  function parseJsonBody(options) {
    if (!options || typeof options.body !== 'string') return null;
    try {
      const data = JSON.parse(options.body);
      return data && typeof data === 'object' ? data : null;
    } catch (_error) {
      return null;
    }
  }

  function jsonResponse(data) {
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: {'Content-Type': 'application/json', 'X-Robo-Teacher-Recovered': 'practice-state'}
    });
  }

  function announce(message) {
    try {
      if (typeof window.setLearningStatus === 'function') window.setLearningStatus(message, 'success');
    } catch (_error) {}
  }

  async function fetchPracticeSnapshot(body) {
    if (!body?.session_token) return null;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);
    try {
      const response = await nativeFetch(`${PRACTICE_PATH}language`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
        body: JSON.stringify({
          session_token: body.session_token,
          language: language?.value || 'English'
        }),
        signal: controller.signal
      });
      if (!response.ok) return null;
      const data = await response.json();
      return data && typeof data === 'object' ? data : null;
    } catch (_error) {
      return null;
    } finally {
      clearTimeout(timeout);
    }
  }

  function recoveredAnswer(snapshot) {
    if (!snapshot?.answered || !snapshot.feedback) return null;
    const attempted = Number(snapshot.attempted || 0);
    const score = Number(snapshot.score || 0);
    const total = Number(snapshot.total_questions || 0);
    const feedback = snapshot.feedback;
    return {
      correct: Boolean(feedback.correct),
      message: feedback.message || '',
      expected_answer: feedback.expected_answer,
      correct_answer_label: feedback.correct_answer_label,
      explanation: feedback.explanation || '',
      score,
      attempted,
      percentage: attempted ? Math.round(score / attempted * 100) : 0,
      completed: Boolean(snapshot.summary) || (total > 0 && attempted >= total),
      summary: snapshot.summary,
      recovered: true
    };
  }

  async function recover(action, body) {
    const snapshot = await fetchPracticeSnapshot(body);
    if (!snapshot) return null;

    if (action === 'answer') {
      const answer = recoveredAnswer(snapshot);
      if (!answer) return null;
      announce('Practice answer restored after a connection delay');
      return jsonResponse(answer);
    }

    if (action === 'next') {
      if (snapshot.summary && snapshot.answered) {
        // The final answer may have reached the server even if its response was
        // lost. Let app.js finish its current call, then replace the transient
        // question view with the already-computed results.
        setTimeout(() => {
          try {
            if (typeof window.renderPracticeResults === 'function') {
              window.renderPracticeResults(snapshot.summary);
              announce('Practice results restored');
            }
          } catch (_error) {}
        }, 0);
        return jsonResponse({...snapshot, recovered: true});
      }

      // An unanswered current question means the server has already advanced,
      // or the learner is still on the same safe question. Returning it is
      // idempotent and never skips an assessment item.
      if (!snapshot.answered) {
        announce('Practice question restored after a connection delay');
        return jsonResponse({...snapshot, recovered: true});
      }
    }
    return null;
  }

  window.fetch = async function resilientFetch(input, options) {
    const action = practiceAction(input);
    if (!action) return nativeFetch(input, options);

    const body = parseJsonBody(options);
    try {
      const response = await nativeFetch(input, options);
      if (response.status !== 409) return response;
      return (await recover(action, body)) || response;
    } catch (error) {
      // A mobile timeout or transient fetch failure can happen after the server
      // accepted the request. Reconcile against server state before telling the
      // learner to retry; never resend the learner's answer automatically.
      const recovered = await recover(action, body);
      if (recovered) return recovered;
      throw error;
    }
  };
})();
