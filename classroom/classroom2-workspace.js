/* Presentation helpers reuse the real classroom handlers and retain all state. */
(() => {
  const classroom = document.getElementById('classroom');
  const voiceStatus = document.getElementById('teacherVoiceStatus');
  const business = document.getElementById('businessDetails');
  if (!classroom) return;

  document.querySelectorAll('[data-classroom-action]').forEach(button => {
    button.addEventListener('click', () => {
      const target = document.getElementById(button.dataset.classroomAction);
      if (target?.id === 'question') target.focus();
      else target?.click();
    });
  });

  function syncScreen() {
    if (business) business.open = classroom.classList.contains('hidden');
  }
  new MutationObserver(syncScreen).observe(classroom, { attributes: true, attributeFilter: ['class'] });
  syncScreen();

  // Keep the detailed learning status as the sole idle indicator. Real speech
  // and playback status remains visible when the teacher is doing something.
  if (voiceStatus) {
    const syncVoice = () => {
      voiceStatus.hidden = voiceStatus.textContent.trim().toLowerCase() === 'ready';
    };
    new MutationObserver(syncVoice).observe(voiceStatus, { childList: true, subtree: true, characterData: true });
    syncVoice();
  }
})();
