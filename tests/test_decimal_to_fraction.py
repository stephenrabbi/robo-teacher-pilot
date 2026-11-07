"""Decimal conversion uses exact hundredths and reduces the answer."""
from fractions import Fraction
import unittest
from unittest.mock import patch

import practice_generator


class DecimalToFractionTests(unittest.TestCase):
    def test_all_generated_hundredths(self):
        for value in range(1, 100):
            with self.subTest(value=value), patch.object(
                practice_generator, "_pick", return_value=True
            ), patch.object(practice_generator, "_int", return_value=value):
                question, hint, answer, explanation = practice_generator.generate_question("Fractions", "Medium")
                self.assertIn(f"{value/100:.2f}", question)
                self.assertEqual(Fraction(answer), Fraction(value, 100))
                self.assertEqual(answer, str(Fraction(value, 100)))
                self.assertIn("hundredths", hint)
                self.assertIn(f"{value}/100", explanation)

    def test_existing_addition_is_retained(self):
        with patch.object(practice_generator, "_pick", side_effect=[False, 2, 4]), patch.object(
            practice_generator, "_int", side_effect=[1, 1]
        ):
            question, _, answer, _ = practice_generator.generate_question("Fractions", "Medium")
            self.assertIn("1/2 + 1/4", question)
            self.assertEqual(answer, "3/4")


if __name__ == "__main__":
    unittest.main()
