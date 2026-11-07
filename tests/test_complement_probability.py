"""Complementary probability covers exactly the outcomes outside an event."""
from fractions import Fraction
import unittest
from unittest.mock import patch

import practice_generator


class ComplementProbabilityTests(unittest.TestCase):
    def test_complements_for_every_bag(self):
        for red in range(1, 11):
            for blue in range(2, 13):
                with self.subTest(red=red, blue=blue), patch.object(
                    practice_generator, "_int", side_effect=[red, blue]
                ):
                    question, hint, answer, explanation = practice_generator.generate_question(
                        "Probability", "Challenge"
                    )
                    self.assertEqual(Fraction(answer) + Fraction(red, red + blue), 1)
                    self.assertEqual(Fraction(answer), Fraction(blue, red + blue))
                    self.assertIn("not red", question)
                    self.assertIn("1 - P(red)", hint)
                    self.assertIn(f"{blue}/{red + blue}", explanation)

    def test_other_difficulties_keep_direct_probability(self):
        for level in ("Easy", "Medium"):
            with self.subTest(level=level), patch.object(
                practice_generator, "_int", side_effect=[2, 3]
            ):
                question, _, answer, _ = practice_generator.generate_question("Probability", level)
                self.assertIn("selecting red", question)
                self.assertEqual(answer, "2/5")


if __name__ == "__main__":
    unittest.main()
