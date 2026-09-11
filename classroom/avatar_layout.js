(() => {
  if (document.getElementById('robo-teacher-compact-avatar-layout')) return;

  const style = document.createElement('style');
  style.id = 'robo-teacher-compact-avatar-layout';
  style.textContent = `
    @media (min-width: 901px) {
      .classroom-screen:not(.teacher-min) {
        grid-template-columns: minmax(280px, 310px) minmax(0, 1fr) !important;
      }
      .teacher-panel:not(.minimized) {
        padding: 15px;
      }
      .teacher-panel:not(.minimized) .teacher-avatar {
        height: 390px !important;
      }
      .teacher-panel:not(.minimized) .teacher-caption {
        font-size: 13px;
        line-height: 1.45;
      }
    }

    @media (max-width: 900px) {
      .classroom-screen,
      .classroom-screen.teacher-min {
        grid-template-columns: 1fr !important;
      }

      .teacher-panel:not(.minimized) {
        height: auto !important;
        min-height: 0;
        display: grid;
        grid-template-columns: 96px minmax(0, 1fr);
        grid-template-areas:
          "portrait toolbar"
          "portrait caption";
        column-gap: 12px;
        row-gap: 4px;
        align-items: center;
        padding: 11px 12px;
        border-radius: 18px;
      }

      .teacher-panel:not(.minimized) .teacher-toolbar {
        grid-area: toolbar;
        margin: 0;
        min-width: 0;
      }

      .teacher-panel:not(.minimized) .teacher-portrait {
        grid-area: portrait;
        align-self: center;
      }

      .teacher-panel:not(.minimized) .teacher-avatar-stage {
        width: 96px;
        max-width: 96px;
        margin: 0;
      }

      .teacher-panel:not(.minimized) .teacher-avatar {
        width: 96px !important;
        height: 112px !important;
        border-radius: 15px;
        object-fit: cover;
        object-position: center top;
      }

      .teacher-panel:not(.minimized) .teacher-caption {
        grid-area: caption;
        margin: 4px 0 0;
        text-align: left;
        font-size: 12px;
        line-height: 1.35;
      }

      .teacher-panel:not(.minimized) .teacher-actions {
        gap: 5px;
        flex-wrap: wrap;
      }

      .teacher-panel:not(.minimized) .teacher-actions select,
      .teacher-panel:not(.minimized) .teacher-actions button,
      .teacher-panel:not(.minimized) .teacher-voice-status {
        min-height: 38px;
        font-size: 12px;
      }

      .teacher-panel:not(.minimized) .hands-free-help,
      .teacher-panel:not(.minimized) .hands-free-heard {
        grid-column: 1 / -1;
      }
    }

    @media (max-width: 520px) {
      .teacher-panel:not(.minimized) {
        grid-template-columns: 78px minmax(0, 1fr);
        column-gap: 10px;
        padding: 10px;
      }
      .teacher-panel:not(.minimized) .teacher-avatar-stage,
      .teacher-panel:not(.minimized) .teacher-avatar {
        width: 78px !important;
        max-width: 78px;
      }
      .teacher-panel:not(.minimized) .teacher-avatar {
        height: 94px !important;
      }
    }
  `;
  document.head.appendChild(style);
})();
