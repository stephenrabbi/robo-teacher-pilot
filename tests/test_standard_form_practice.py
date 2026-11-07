"""Standard-form multiplication keeps both magnitude and a valid coefficient."""
from fractions import Fraction
import unittest
from unittest.mock import patch

import practice_generator


class StandardFormPracticeTests(unittest.TestCase):
    def test_products_below_at_and_above_ten(self):
        for coefficient, multiplier, expected in (
            (11, 2, "2.2*10^3"),
            (25, 4, "1*10^4"),
            (80, 3, "2.4*10^4"),
            (99, 8, "7.92*10^4"),
        ):
            with self.subTest(coefficient=coefficient, multiplier=multiplier), patch.object(
                practice_generator, "_int", side_effect=[coefficient, 3, multiplier]
            ):
                question, hint, answer, explanation = practice_generator.generate_question(
                    "Standard Form", "Challenge"
                )
                self.assertEqual(answer, expected)
                mantissa, exponent = answer.split("*10^")
                self.assertGreaterEqual(Fraction(mantissa), 1)
                self.assertLess(Fraction(mantissa), 10)
                self.assertEqual(
                    Fraction(mantissa) * 10 ** int(exponent),
                    coefficient * multiplier * 100,
                )
                self.assertIn("standard form", question)
                self.assertIn(mantissa + " × 10^" + exponent, explanation)

    def test_easy_and_medium_questions_retain_their_values(self):
        for level, expected in (("Easy", "2.5*10^3"), ("Medium", "2500")):
            with self.subTest(level=level), patch.object(
                practice_generator, "_int", side_effect=[25, 3]
            ):
                self.assertEqual(
                    practice_generator.generate_question("Standard Form", level)[2], expected
                )


if __name__ == "__main__":
    unittest.main()
