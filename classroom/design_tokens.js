(() => {
  if (document.getElementById('roboTeacherDesignTokens')) return;

  const style = document.createElement('style');
  style.id = 'roboTeacherDesignTokens';
  style.textContent = `
    :root {
      --rt-navy-950: #081a33;
      --rt-navy-900: #102744;
      --rt-navy-800: #17355e;
      --rt-navy-700: #173f76;
      --rt-blue-500: #67a6ff;
      --rt-gold-500: #d39a27;
      --rt-green-700: #075d45;
      --rt-text-900: #10203a;
      --rt-text-700: #34445c;
      --rt-text-600: #4f6077;
      --rt-surface-50: #f7fbff;
      --rt-surface-100: #eef4fb;
      --rt-line-200: #d6e1ef;
      --rt-line-400: #9eb9da;
      --rt-radius-sm: 10px;
      --rt-radius-md: 12px;
      --rt-radius-lg: 16px;
      --rt-radius-xl: 22px;
      --rt-space-1: 4px;
      --rt-space-2: 8px;
      --rt-space-3: 12px;
      --rt-space-4: 16px;
      --rt-space-5: 20px;
      --rt-space-6: 24px;
      --rt-control-min: 44px;
      --rt-focus-ring: 3px solid var(--rt-blue-500);
      --rt-focus-offset: 2px;
    }

    .class-tools.nav-redesigned > button,
    .class-tools.nav-redesigned > .class-tools-more > summary,
    .input-tools-more > summary,
    .class-tools-more-menu button,
    .input-tools-menu button,
    .contextual-lesson-actions button,
    #dataSaverButton {
      border-radius: var(--rt-radius-md);
    }

    .class-tools-more-menu,
    .input-tools-menu {
      border-radius: var(--rt-radius-lg);
    }

    .speech-card {
      border-radius: var(--rt-radius-xl);
    }

    .contextual-lesson-actions {
      border-top-color: var(--rt-line-200);
    }

    .contextual-lesson-actions button {
      background: var(--rt-surface-100);
      color: var(--rt-text-900);
    }

    .data-saver-notice {
      border-color: var(--rt-line-400);
      border-radius: var(--rt-radius-md);
      background: var(--rt-surface-50);
      color: var(--rt-navy-800);
    }

    :where(
      .class-tools.nav-redesigned > button,
      .class-tools.nav-redesigned summary,
      .class-tools-more-menu button,
      .input-tools-menu button,
      .contextual-lesson-actions button,
      #dataSaverButton,
      #startLearning,
      #resumeLearning,
      #readAnswer,
      #nextLessonStep,
      #previousLessonStep,
      #replayLessonStep,
      #askLessonQuestion,
      #startPractice,
      #nextPractice,
      #practiceForm button,
      #closePractice,
      #closeProgress
    ):focus-visible {
      outline: var(--rt-focus-ring);
      outline-offset: var(--rt-focus-offset);
    }

    @media (max-width: 600px) {
      :where(
        .class-tools.nav-redesigned > button,
        .class-tools.nav-redesigned summary,
        .class-tools-more-menu button,
        .input-tools-menu button,
        .contextual-lesson-actions button,
        #dataSaverButton
      ) {
        min-height: var(--rt-control-min);
      }
    }
  `;
  document.head.appendChild(style);
})();
