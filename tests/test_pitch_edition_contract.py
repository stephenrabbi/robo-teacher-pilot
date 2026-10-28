"""Non-destructive contract checks for Robo-Teacher Pitch Edition UI.

Run from repository root: python -m unittest discover -s tests -p 'test_pitch_edition_contract.py'
"""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
HTML = ROOT / "classroom" / "index.html"
CSS = ROOT / "classroom" / "pitch-edition.css"


class PitchEditionContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML.read_text(encoding="utf-8")
        cls.css = CSS.read_text(encoding="utf-8")

    def test_stylesheet_link_is_after_legacy_css(self):
        links = re.findall(r'<link\s+rel="stylesheet"\s+href="([^"]+)"', self.html)
        self.assertGreaterEqual(len(links), 3)
        self.assertEqual(links[-1].split("?")[0], "/classroom/pitch-edition.css")
        self.assertTrue(CSS.is_file())

    def test_expected_screen_anchors_are_preserved(self):
        for anchor in ("welcome", "classroom", "practiceArea", "dailyPlanArea",
                       "progressArea", "teacherDashboard", "learnerCodeManager",
                       "teacherPanel", "founderPanel"):
            with self.subTest(anchor=anchor):
                self.assertRegex(self.html, r'\bid="' + anchor + r'"')

    def test_existing_scripts_remain_loaded(self):
        for path in ("compliance.js", "app.js", "classroom2-workspace.js"):
            self.assertIn("/classroom/" + path, self.html)

    def test_core_brand_and_pilot_assets_preserved(self):
        for filename in ("robo-teacher-logo.png", "real-students-classroom-welcome.jpg",
                         "herbert-stephen-founder.jpg"):
            self.assertIn(filename, self.html)
            self.assertTrue((ROOT / "classroom" / "assets" / filename).is_file(),
                            msg="Missing classroom asset: " + filename)

    def test_approved_option_one_copy_and_layout(self):
        """Stop accidental regressions back to the rejected old welcome screen."""
        self.assertIn("Big ideas.", self.html)
        self.assertIn("Small steps.", self.html)
        self.assertIn("Your kind of learning.", self.html)
        self.assertIn('id="welcomeStartGuideTitle"', self.html)
        self.assertIn("How to get started", self.html)
        self.assertIn('id="hearFounder"', self.html)
        self.assertIn('id="startLearning"', self.html)
        self.assertIn('data-class-choice="JSS1"', self.html)
        self.assertIn('data-class-choice="JSS2"', self.html)
        self.assertIn('data-class-choice="JSS3"', self.html)
        self.assertIn("background:#e8e2ff", self.css)
        self.assertIn("background:#fff744", self.css)

    def test_pitch_controls_preserve_native_onboarding(self):
        """The visual class choices must keep the native control usable by app.js."""
        js = (ROOT / "classroom" / "pitch-edition.js").read_text(encoding="utf-8")
        self.assertIn('id="learnerClass"', self.html)
        self.assertIn('id="learnerNickname"', self.html)
        self.assertIn('id="learnerConsent"', self.html)
        self.assertIn('id="generateLearnerCode"', self.html)
        self.assertIn('select.dispatchEvent(new Event("change"', js)
        self.assertIn("pitch-edition.js", self.html)

    def test_mobile_breakpoints_and_accessibility(self):
        self.assertRegex(self.html, r'name="viewport"')
        for width in ("900px", "600px"):
            self.assertIn(width, self.css)
        self.assertIn(":focus-visible", self.css)
        self.assertIn("prefers-reduced-motion", self.css)

    def test_no_script_or_external_asset_in_new_style_layer(self):
        self.assertNotIn("<script", self.css.lower())
        self.assertNotIn("@import", self.css.lower())
        self.assertNotIn("url(http", self.css.lower())


if __name__ == "__main__":
    unittest.main()
