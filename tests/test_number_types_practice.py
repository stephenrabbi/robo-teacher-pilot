"""Classification practice includes rational and irrational square roots."""
import math
import unittest
from unittest.mock import patch

import practice_generator


class NumberTypesPracticeTests(unittest.TestCase):
    def test_perfect_square_roots_are_rational(self):
        for value in range(2, 13):
            with self.subTest(value=value), patch.object(
                practice_generator, "_pick", return_value=True
            ), patch.object(practice_generator, "_int", return_value=value):
                question, _, answer, explanation = practice_generator.generate_question(
                    "Rational & Irrational Numbers", "Easy"
                )
                self.assertIn(f"√{value * value}", question)
                self.assertEqual(answer, "rational")
                self.assertIn(f"{value}/1", explanation)

    def test_non_square_roots_are_irrational(self):
        for value in range(2, 100):
            if math.isqrt(value) ** 2 == value:
                continue
            with self.subTest(value=value), patch.object(
                practice_generator, "_pick", return_value=False
            ), patch.object(practice_generator, "_int", return_value=value):
                question, _, answer, explanation = practice_generator.generate_question(
                    "Rational & Irrational Numbers", "Challenge"
                )
                self.assertIn(f"√{value}", question)
                self.assertEqual(answer, "irrational")
                self.assertIn("cannot be written as a ratio of integers", explanation)


if __name__ == "__main__":
    unittest.main()
