"""Structural safety checks for the isolated Classroom 2.0 welcome stylesheet.
Run: python -m unittest discover -s tests -p 'test_classroom2_welcome_contract.py'
These checks do not replace browser or device tests.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "classroom/index.html").read_text(encoding="utf-8")
STYLES = (ROOT / "classroom/classroom2-welcome.css").read_text(encoding="utf-8")

class Classroom2WelcomeContract(unittest.TestCase):
    def test_styling_loaded_after_existing_stylesheet(self):
        self.assertIn("/classroom/classroom2-welcome.css", HTML)
        self.assertLess(HTML.index("/classroom/styles.css"), HTML.index("/classroom/classroom2-welcome.css"))

    def test_critical_onboarding_and_voice_ids(self):
        needed = ("welcome", "founderPanel", "learnerNickname", "learnerCode",
                  "generateLearnerCode", "learnerClass", "learnerConsent",
                  "startLearning", "hearFounder", "resumeLearning", "onboardingError")
        for element_id in needed:
            with self.subTest(element_id=element_id):
                self.assertRegex(HTML, r'id=["\']' + element_id + r'["\']')

    def test_original_visual_assets(self):
        for filename in ("robo-teacher-logo.png", "real-students-classroom-welcome.jpg",
                         "herbert-stephen-founder.jpg", "herbert-stephen-founder-speaking.jpg"):
            with self.subTest(filename=filename):
                self.assertIn(filename, HTML)

    def test_css_explicitly_scoped_to_welcome(self):
        rules = re.findall(r'([^{}]+)\{[^{}]*\}', re.sub(r'/\*.*?\*/', '', STYLES, flags=re.S))
        for selector in rules:
            selector = selector.strip()
            if selector.startswith('@'):
                continue
            # Do not split selector commas inside :is(...).
            selector = re.sub(r':is\([^)]*\)', ':is(controls)', selector)
            for part in selector.split(','):
                part = part.strip()
                if part.startswith('@') or part in ('from', 'to') or re.fullmatch(r'[\d.]+%', part):
                    continue
                with self.subTest(selector=part):
                    self.assertTrue(part.startswith('#welcome') or (part.startswith('body:has(#welcome') and ('#privacyConsentBanner' in part or part.endswith(')'))), part)

    def test_no_inline_script_replacement(self):
        self.assertIn('/classroom/app.js', HTML)
        self.assertIn('/classroom/supabase_classroom_optin.js', HTML)

if __name__ == "__main__":
    unittest.main()
