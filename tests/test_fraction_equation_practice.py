"""Fraction equation challenges clear a grouped numerator correctly."""
from fractions import Fraction
import unittest
from unittest.mock import patch

import practice_generator


class FractionEquationTests(unittest.TestCase):
    def test_grouped_numerator_solutions_by_substitution(self):
        for denominator in range(2, 10):
            for total in range(2, 21):
                for constant in range(1, 11):
                    with self.subTest(d=denominator, total=total, c=constant), patch.object(
                        practice_generator, "_int", side_effect=[denominator, total, constant]
                    ):
                        question, hint, answer, explanation = practice_generator.generate_question(
                            "Equations Involving Fractions", "Challenge"
                        )
                        self.assertEqual(Fraction(int(answer) + constant, denominator), total)
                        self.assertIn(f"(x + {constant})/{denominator}", question)
                        self.assertIn("Multiply both sides", hint)
                        self.assertIn("Step 3: Check:", explanation)

    def test_existing_difficulties_keep_their_equation_pattern(self):
        for level in ("Easy", "Medium"):
            with self.subTest(level=level), patch.object(
                practice_generator, "_int", side_effect=[3, 4, 2]
            ):
                question, _, answer, _ = practice_generator.generate_question(
                    "Equations Involving Fractions", level
                )
                self.assertEqual(question, "Solve x/3 + 2 = 6.")
                self.assertEqual(answer, "12")


if __name__ == "__main__":
    unittest.main()
