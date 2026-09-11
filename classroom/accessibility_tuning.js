(() => {
  if (document.getElementById('robo-teacher-accessibility-tuning')) return;

  const style = document.createElement('style');
  style.id = 'robo-teacher-accessibility-tuning';
  style.textContent = `
    /* Stronger normal-text contrast on light learner surfaces. */
    .canvas-empty p,
    .whiteboard-hint,
    .practice-context,
    .progress-empty,
    .progress-stats span,
    .topic-progress span,
    .recent-sessions span,
    .learning-path-key,
    .learning-path-topic span,
    .weekly-summary em,
    .weekly-insights span,
    .qa-summary span,
    .teacher-weekly-stats span,
    .teacher-dashboard-actions label,
    .teacher-insights span,
    .teacher-trend-bars span {
      color: #4f6077;
    }

    /* Keyboard focus must also cover the new disclosure controls. */
    summary:focus-visible {
      outline: 3px solid #67a6ff;
      outline-offset: 2px;
    }

    .class-tools-more > summary,
    .input-tools-more > summary {
      min-height: 44px;
      min-width: 44px;
    }
  `;
  document.head.appendChild(style);
})();
