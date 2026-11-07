"""Formula challenges isolate the subject before substituting values."""
from fractions import Fraction
import unittest
from unittest.mock import patch

import practice_generator


class FormulaePracticeTests(unittest.TestCase):
    def test_all_triangle_dimensions_preserve_the_area(self):
        for base in range(2, 16):
            for height in range(2, 21):
                with self.subTest(base=base, height=height), patch.object(
                    practice_generator, "_int", side_effect=[base, height]
                ):
                    question, hint, answer, explanation = practice_generator.generate_question(
                        "Formulae & Change of Subject", "Challenge"
                    )
                    area = Fraction(base * height, 2)
                    self.assertEqual(Fraction(base * int(answer), 2), area)
                    self.assertIn("Make h the subject", question)
                    self.assertIn("then divide by b", hint)
                    self.assertIn("h = 2A/b", explanation)

    def test_other_difficulties_keep_perimeter_rearrangement(self):
        for level in ("Easy", "Medium"):
            with self.subTest(level=level), patch.object(
                practice_generator, "_int", side_effect=[8, 5]
            ):
                question, _, answer, _ = practice_generator.generate_question(
                    "Formulae & Change of Subject", level
                )
                self.assertIn("P = 2(l + w)", question)
                self.assertEqual(answer, "8")


if __name__ == "__main__":
    unittest.main()
