"""Fraction comparison depends on size, not presentation order."""
from fractions import Fraction
import unittest
from unittest.mock import patch

import practice_generator


class FractionComparisonTests(unittest.TestCase):
    def test_both_orders_for_all_generated_fractions(self):
        for numerator in range(1, 6):
            for small in range(6, 13):
                for large in range(13, 21):
                    for reverse in (False, True):
                        with patch.object(practice_generator, "_pick", side_effect=[True, reverse]), patch.object(
                            practice_generator, "_int", side_effect=[numerator, small, large]
                        ):
                            question, _, answer, explanation = practice_generator.generate_question("Fractions", "Easy")
                            self.assertEqual(Fraction(answer), max(Fraction(numerator, small), Fraction(numerator, large)))
                            first, second = (large, small) if reverse else (small, large)
                            self.assertIn(f"{numerator}/{first} or {numerator}/{second}", question)
                            self.assertIn(f"{numerator}/{small} is larger", explanation)

    def test_existing_addition_is_retained(self):
        with patch.object(practice_generator, "_pick", side_effect=[False, 4]), patch.object(
            practice_generator, "_int", side_effect=[1, 2]
        ):
            question, _, answer, _ = practice_generator.generate_question("Fractions", "Easy")
            self.assertIn("1/4 + 2/4", question)
            self.assertEqual(answer, "3/4")


if __name__ == "__main__":
    unittest.main()
