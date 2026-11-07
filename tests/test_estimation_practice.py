"""Estimation uses whole-number place value and school rounding at halfway."""
from fractions import Fraction
import unittest
from unittest.mock import patch

import practice_generator


class EstimationPracticeTests(unittest.TestCase):
    def test_rounding_below_at_and_above_halfway(self):
        for level, unit in (("Easy", 10), ("Medium", 100), ("Challenge", 1000)):
            for value in (unit * 10 + unit // 2 - 1, unit * 10 + unit // 2,
                          unit * 10 + unit // 2 + 1, 99999):
                with self.subTest(level=level, value=value), patch.object(
                    practice_generator, "_int", return_value=value
                ), patch.object(practice_generator, "_pick", return_value=False):
                    question, hint, answer, explanation = practice_generator.generate_question("Estimation", level)
                    self.assertEqual(int(answer), ((value + unit // 2) // unit) * unit)
                    self.assertIn(f"nearest {unit:,}", question)
                    self.assertIn("halfway", hint)
                    self.assertIn("halfway point", explanation)
                    self.assertIn("books", explanation)

    def test_step_estimates_convert_centimetres_to_metres(self):
        for steps in range(10, 41):
            for step_cm in range(50, 81):
                with patch.object(practice_generator, "_pick", return_value=True), patch.object(
                    practice_generator, "_int", side_effect=[steps, step_cm]
                ):
                    question, hint, answer, explanation = practice_generator.generate_question(
                        "Estimation", "Challenge"
                    )
                    self.assertEqual(Fraction(answer), Fraction(steps * step_cm, 100))
                    self.assertIn(f"{steps} equal steps", question)
                    self.assertIn(f"about {step_cm} cm", question)
                    self.assertIn("centimetres to metres", hint)
                    self.assertIn("step length is approximate", explanation)

    def test_decimals_topic_keeps_its_existing_generator(self):
        with patch.object(practice_generator, "_decimals", return_value=("existing",)) as decimals:
            self.assertEqual(
                practice_generator.generate_question("Decimals & Approximation", "Easy"), ("existing",)
            )
            decimals.assert_called_once_with("Easy")


if __name__ == "__main__":
    unittest.main()
