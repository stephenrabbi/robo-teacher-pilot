"""Fraction division uses the reciprocal of the divisor, not the dividend."""
from fractions import Fraction
import unittest
from unittest.mock import patch

import practice_generator


class FractionDivisionTests(unittest.TestCase):
    def test_all_generated_division_cases(self):
        for a in range(2, 10):
            for b in range(3, 11):
                for c in range(2, 10):
                    for d in range(3, 11):
                        with patch.object(practice_generator, "_pick", return_value=True), patch.object(
                            practice_generator, "_int", side_effect=[a, b, c, d]
                        ):
                            question, hint, answer, explanation = practice_generator.generate_question(
                                "Fractions", "Challenge"
                            )
                            self.assertEqual(Fraction(answer) * Fraction(c, d), Fraction(a, b))
                            self.assertIn(f"{a}/{b} ÷ {c}/{d}", question)
                            self.assertIn("reciprocal of the second", hint)
                            self.assertIn(f"{a}/{b} × {d}/{c}", explanation)

    def test_multiplication_is_still_available(self):
        with patch.object(practice_generator, "_pick", return_value=False), patch.object(
            practice_generator, "_int", side_effect=[2, 3, 4, 5]
        ):
            question, _, answer, _ = practice_generator.generate_question("Fractions", "Challenge")
            self.assertIn("2/3 × 4/5", question)
            self.assertEqual(answer, "8/15")


if __name__ == "__main__":
    unittest.main()
