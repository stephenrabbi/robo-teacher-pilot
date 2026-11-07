"""Inverse variation preserves the product rather than the ratio."""
from fractions import Fraction
import unittest
from unittest.mock import patch

import practice_generator


class VariationPracticeTests(unittest.TestCase):
    def test_inverse_variation_preserves_product_for_every_generated_case(self):
        for x1 in range(2, 9):
            for y1 in range(3, 13):
                for x2 in range(9, 21):
                    with self.subTest(x1=x1, y1=y1, x2=x2), patch.object(
                        practice_generator, "_int", side_effect=[x1, y1, x2]
                    ):
                        question, hint, answer, explanation = practice_generator.generate_question(
                            "Ratio, Proportion & Variation", "Challenge"
                        )
                        self.assertEqual(Fraction(answer) * x2, x1 * y1)
                        self.assertLess(Fraction(answer), y1)
                        self.assertIn("inversely", question)
                        self.assertIn("xy is constant", hint)
                        self.assertIn("y = k/x", explanation)

    def test_direct_variation_is_retained_at_other_difficulties(self):
        for level in ("Easy", "Medium"):
            with self.subTest(level=level), patch.object(
                practice_generator, "_int", side_effect=[3, 4, 12]
            ):
                question, _, answer, _ = practice_generator.generate_question(
                    "Ratio, Proportion & Variation", level
                )
                self.assertIn("directly", question)
                self.assertEqual(answer, "16")


if __name__ == "__main__":
    unittest.main()
