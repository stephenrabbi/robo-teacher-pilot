"""Regression contracts for the responsive Robo-Teacher classroom.

These checks do not replace live viewport or speech-output tests.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "classroom" / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "classroom" / "classroom2.css").read_text(encoding="utf-8")


class ResponsiveClassroomContract(unittest.TestCase):
    def test_core_learner_controls_are_preserved(self):
        controls = ("classroom", "teacherPanel", "canvas", "canvasAnswer",
                    "chatForm", "question", "micButton", "uploadButton",
                    "imageUpload", "cameraCapture", "readAnswer",
                    "language", "practiceButton", "progressButton")
        for control in controls:
            with self.subTest(control=control):
                self.assertEqual(
                    len(re.findall(r'\\bid="' + re.escape(control) + r'"', HTML)), 1,
                    "Missing or duplicated interactive control: " + control)

    def test_image_capture_remains_user_controlled(self):
        self.assertIn('id="cameraCapture"', HTML)
        self.assertIn('capture="environment"', HTML)
        self.assertIn('id="imageUpload"', HTML)

    def test_mobile_breakpoints_exist(self):
        for breakpoint in ("767px", "600px", "380px"):
            with self.subTest(breakpoint=breakpoint):
                self.assertIn(breakpoint, CSS)
        self.assertIn("#classroom #question", CSS)
        self.assertIn("font-size:16px", CSS)

    def test_accessibility_guards(self):
        self.assertIn("#classroom button:focus-visible", CSS)
        self.assertIn("min-height:44px", CSS)
        self.assertIn('aria-label="Teaching language"', HTML)
        self.assertIn('aria-label="Start voice question"', HTML)
        self.assertIn('aria-live="polite"', HTML)

    def test_classroom_stylesheet_cache_key(self):
        self.assertIn("classroom2.css?v=20261030-mobile-classroom1", HTML)


if __name__ == "__main__":
    unittest.main()
