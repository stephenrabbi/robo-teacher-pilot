(() => {
  let cachedMasterySummary = null;
  let activeIntervention = null;

  async function masteryRequest(path, payload) {
    const token = await ensureSession();
    const response = await fetch(`/api/classroom/mastery/${path}`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
      body: JSON.stringify({session_token: token, class_level: learnerClass.value, ...payload})
    });
    const data = await response.json();
    if (response.status === 401) sessionToken = null;
    if (!response.ok) throw new Error(data.detail || 'Mastery memory unavailable');
    return data;
  }

  function topicHint() {
    const candidates = [
      currentPractice?.topic,
      currentPracticeSummary?.topic,
      currentProgress?.recommended_topic,
      practiceTopic?.value
    ];
    return candidates.find(value => typeof value === 'string' && value.trim()) || '';
  }

  function lessonText() {
    return currentLesson?.text || canvasAnswer?.innerText?.trim() || '';
  }

  window.roboTeacherSetActiveIntervention = function (plan) {
    const category = String(plan?.misconception_category || '').trim();
    const strategy = String(plan?.teaching_strategy || '').trim();
    const topic = String(plan?.topic || '').trim();
    activeIntervention = category && strategy && topic ? {category, strategy, topic} : null;
    return Boolean(activeIntervention);
  };

  window.roboTeacherClearActiveIntervention = function () {
    activeIntervention = null;
  };

  window.roboTeacherMasteryRecord = async function ({correct, stage, checkId, question='', selectedChoice='', correctChoice='', feedback=''}) {
    if (!checkId) return null;
    const hint = topicHint();
    const intervention = activeIntervention && (!hint || hint === activeIntervention.topic) ? activeIntervention : null;
    try {
      const data = await masteryRequest('event', {
        correct: Boolean(correct),
        // A check immediately following a planner-selected intervention is itself
        // a reteach check, even though it entered through the ordinary Check UI.
        stage: intervention ? 'reteach' : (stage === 'reteach' ? 'reteach' : 'initial'),
        check_id: checkId,
        lesson_text: lessonText(),
        topic_hint: hint,
        question: correct ? '' : String(question || '').slice(0, 1000),
        selected_choice: correct ? '' : String(selectedChoice || '').slice(0, 500),
        correct_choice: correct ? '' : String(correctChoice || '').slice(0, 500),
        feedback: correct ? '' : String(feedback || '').slice(0, 1500),
        intervention_category: intervention?.category || '',
        intervention_strategy: intervention?.strategy || ''
      });
      if (data.summary) cachedMasterySummary = data.summary;
      if (intervention && data?.stored) activeIntervention = null;
      return data;
    } catch (_error) {
      return null;
    }
  };

  function memoryByTopic(summary) {
    return new Map((summary?.topics || []).map(item => [item.topic, item]));
  }

  function mergeLearnerProgress(progress, summary) {
    if (!progress || !summary) return progress;
    const memory = memoryByTopic(summary);
    const flat = [];
    (progress.learning_path || []).forEach(term => {
      (term.topics || []).forEach(item => {
        const saved = memory.get(item.topic);
        if (saved) {
          item.mastery_memory_state = saved.state;
          item.mastery_memory_confidence = saved.confidence;
          item.mastery_checks = saved.checks;
          item.last_mastery_at = saved.last_seen;
          item.misconception = saved.misconception || null;
          item.misconception_label = saved.misconception_label || null;
          item.teaching_strategy = saved.teaching_strategy || null;
          item.strategy_effectiveness = saved.strategy_effectiveness || null;
          if (saved.state === 'mastered') {
            item.mastery_status = 'mastered';
            item.status = 'mastered';
            item.mastery_estimate = Math.max(Number(item.mastery_estimate) || 0, 85);
          } else if (saved.state === 'needs_support') {
            item.mastery_status = 'needs_support';
            item.status = 'needs_practice';
            item.mastery_estimate = Math.min(Number(item.mastery_estimate) || 45, 45);
          } else if (item.mastery_status === 'not_started') {
            item.mastery_status = 'developing';
            item.status = 'needs_practice';
            item.mastery_estimate = Math.max(Number(item.mastery_estimate) || 0, 60);
          }
        }
        flat.push(item);
      });
    });

    const supportTopic = summary.needs_support_topics?.[0];
    if (supportTopic) {
      progress.recommended_topic = supportTopic;
      progress.focus_topic = supportTopic;
      progress.recommendation_reason = 'mastery_memory';
      progress.recommended_difficulty = 'Easy';
      const match = flat.find(item => item.topic === supportTopic);
      if (match) match.status = 'recommended';
    } else {
      const currentSaved = memory.get(progress.recommended_topic);
      if (currentSaved?.state === 'mastered') {
        const next = flat.find(item => item.mastery_status !== 'mastered' && item.topic !== progress.recommended_topic);
        if (next) {
          progress.recommended_topic = next.topic;
          progress.focus_topic = next.topic;
          progress.recommendation_reason = 'next_after_mastery';
          next.status = 'recommended';
        }
      }
    }
    progress.mastery_memory = summary;
    if (summary.misconception_focus) progress.misconception_focus = summary.misconception_focus;
    return progress;
  }

  if (typeof practiceRequest === 'function') {
    const basePracticeRequest = practiceRequest;
    practiceRequest = async function (path, body) {
      const data = await basePracticeRequest(path, body);
      if (path !== 'progress') return data;
      try {
        cachedMasterySummary = await masteryRequest('summary', {});
        return mergeLearnerProgress(data, cachedMasterySummary);
      } catch (_error) {
        return data;
      }
    };
  }

  function mergeTeacherDashboard(data, memory) {
    if (!data || !memory) return data;
    const byCode = new Map((memory.learners || []).map(item => [item.learner_code, item]));
    (data.learner_rows || []).forEach(row => {
      const saved = byCode.get(row.learner_code);
      if (!saved) return;
      row.mastered_topics = saved.mastered_topics || [];
      row.developing_topics = saved.developing_topics || [];
      row.needs_support_topics = saved.needs_support_topics || [];
      row.support_misconception = saved.support_misconception || null;
      row.teaching_strategy = saved.teaching_strategy || null;
      row.strategy_effectiveness = saved.strategy_effectiveness || null;
      if (saved.support_topic) {
        row.support_topic = saved.support_misconception
          ? `${saved.support_topic} · ${saved.support_misconception}`
          : saved.support_topic;
      }
    });
    if (memory.focus_topic) {
      data.focus_topic = memory.focus_topic;
      data.weakest_topic = memory.focus_topic;
      const effect = memory.focus_strategy_effectiveness || null;
      if (memory.focus_misconception && memory.focus_teaching_strategy) {
        if (effect?.selection_reason === 'worked_before') {
          data.recommendation = `Prioritise ${memory.focus_misconception_topic || memory.focus_topic}. Recurring pattern: ${memory.focus_misconception}. Reuse the intervention that previously produced a correct check: ${memory.focus_teaching_strategy}`;
        } else if (effect?.selection_reason === 'new_after_failure') {
          data.recommendation = `Prioritise ${memory.focus_misconception_topic || memory.focus_topic}. Recurring pattern: ${memory.focus_misconception}. The previous approach did not resolve it; try this different intervention: ${memory.focus_teaching_strategy}`;
        } else {
          data.recommendation = `Prioritise ${memory.focus_misconception_topic || memory.focus_topic}. Recurring pattern: ${memory.focus_misconception}. Suggested intervention: ${memory.focus_teaching_strategy}`;
        }
      } else {
        data.recommendation = `Prioritise ${memory.focus_topic}; recent mastery checks show learners still need support there.`;
      }
    }
    data.misconception_focus = memory.focus_misconception ? {
      topic: memory.focus_misconception_topic || memory.focus_topic,
      label: memory.focus_misconception,
      teaching_tip: memory.focus_teaching_strategy,
      strategy_effectiveness: memory.focus_strategy_effectiveness || null
    } : null;
    data.mastery_memory_synced = memory.storage_synced;
    return data;
  }

  if (typeof fetchTeacherDashboard === 'function') {
    const baseFetchTeacherDashboard = fetchTeacherDashboard;
    fetchTeacherDashboard = async function (accessKey) {
      const data = await baseFetchTeacherDashboard(accessKey);
      try {
        const response = await fetch('/api/classroom/mastery/teacher', {
          method: 'POST',
          headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
          body: JSON.stringify({access_key: accessKey, class_level: teacherClass.value})
        });
        const memory = await response.json();
        if (response.ok) return mergeTeacherDashboard(data, memory);
      } catch (_error) {
        // Teacher View remains usable if mastery memory is temporarily unavailable.
      }
      return data;
    };
  }

  window.roboTeacherMasterySummary = () => cachedMasterySummary;
})();
