"""Regression checks for the staged classroom's direct-arithmetic routing.

Run: python -m unittest tests.test_staging_direct_arithmetic_routing
"""
import pathlib
import re
import unittest

APP_JS = (pathlib.Path(__file__).resolve().parents[1] / "classroom" / "app.js").read_text(encoding="utf-8")

class DirectArithmeticRoutingTests(unittest.TestCase):
    def test_routing_keeps_raw_arithmetic(self):
        self.assertIn("const requestText=directArithmetic ? text :", APP_JS)
        self.assertIn("!interruptedLesson", APP_JS)

    def test_adaptive_context_preserved_for_other_questions(self):
        self.assertIn("${adaptivePromptContext()}", APP_JS)
        self.assertIn("${lessonQuestion}", APP_JS)

    def test_staging_synthetic_module_not_modified(self):
        self.assertIn("robo:practice-completed", (pathlib.Path(__file__).resolve().parents[1] / "classroom" / "supabase_classroom_optin.js").read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
