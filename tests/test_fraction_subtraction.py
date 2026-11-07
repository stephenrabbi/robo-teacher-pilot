"""Fraction subtraction converts both operands to the common denominator."""
from fractions import Fraction
import unittest
from unittest.mock import patch

import practice_generator


class FractionSubtractionTests(unittest.TestCase):
    def test_common_denominators_swapped_operands_and_zero(self):
        for a, d1, b, d2 in ((1, 2, 1, 4), (1, 6, 3, 4), (1, 2, 2, 4), (2, 3, 1, 6)):
            with self.subTest(a=a, d1=d1, b=b, d2=d2), patch.object(
                practice_generator, "_pick", side_effect=[False, d1, d2, True]
            ), patch.object(practice_generator, "_int", side_effect=[a, b]):
                question, hint, answer, explanation = practice_generator.generate_question("Fractions", "Medium")
                self.assertEqual(Fraction(answer), abs(Fraction(a, d1) - Fraction(b, d2)))
                self.assertIn(" - ", question)
                self.assertIn("subtract the numerators", hint)
                self.assertIn("common denominator", explanation)
                self.assertIn("Step 2:", explanation)


if __name__ == "__main__":
    unittest.main()
