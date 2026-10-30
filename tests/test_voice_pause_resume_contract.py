"""Guard read-aloud pause/resume controls against accidental UI regressions.

These structural checks do not replace listening on a physical device.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "classroom" / "app.js").read_text(encoding="utf-8")
HTML = (ROOT / "classroom" / "index.html").read_text(encoding="utf-8")


class VoiceControlContract(unittest.TestCase):
    def test_read_answer_button_exists(self):
        self.assertIn('id="readAnswer"', HTML)

    def test_pause_sets_visible_and_accessible_state(self):
        start = APP.index("async function pauseTeacherAudio()")
        end = APP.index("async function resumeTeacherAudio()", start)
        pause = APP[start:end]
        for marker in (
            "teacherSpeechPaused=true",
            "teacherPanel.classList.add('paused')",
            "teacherVoiceStatus.textContent='Paused'",
            "Continue reading the answer",
            "teacherAudioContext.suspend()",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, pause)

    def test_resume_reactivates_audio_context(self):
        start = APP.index("async function resumeTeacherAudio()")
        resume = APP[start:start + 1050]
        for marker in (
            "await teacherAudioContext.resume()",
            "teacherSpeechPaused=false",
            "setTeacherSpeaking(true)",
        ):
            self.assertIn(marker, resume)

    def test_read_answer_toggles_pause_or_resume_before_restarting(self):
        start = APP.index("readAnswerButton.addEventListener('click'")
        handler = APP[start:start + 440]
        self.assertIn("if(teacherSpeechPaused){await resumeTeacherAudio();return;}", handler)
        self.assertIn("if(teacherPanel.classList.contains('speaking')){await pauseTeacherAudio();return;}", handler)


if __name__ == "__main__":
    unittest.main()
