"""Estimation uses whole-number place value and school rounding at halfway."""
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
                ):
                    question, hint, answer, explanation = practice_generator.generate_question("Estimation", level)
                    self.assertEqual(int(answer), ((value + unit // 2) // unit) * unit)
                    self.assertIn(f"nearest {unit:,}", question)
                    self.assertIn("halfway", hint)
                    self.assertIn("halfway point", explanation)
                    self.assertIn("books", explanation)

    def test_decimals_topic_keeps_its_existing_generator(self):
        with patch.object(practice_generator, "_decimals", return_value=("existing",)) as decimals:
            self.assertEqual(
                practice_generator.generate_question("Decimals & Approximation", "Easy"), ("existing",)
            )
            decimals.assert_called_once_with("Easy")


if __name__ == "__main__":
    unittest.main()
