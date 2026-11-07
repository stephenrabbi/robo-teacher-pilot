"""JSS1 LCM practice extends to three numbers without multiplying blindly."""
import math
import unittest
from unittest.mock import patch

import practice_generator


class ThreeNumberLCMTests(unittest.TestCase):
    def test_every_generated_triple(self):
        for a in range(3, 16):
            for b in range(3, 16):
                for c in range(3, 16):
                    with patch.object(practice_generator, "_pick", return_value=False), patch.object(
                        practice_generator, "_int", side_effect=[a, b, c]
                    ):
                        question, _, answer, explanation = practice_generator.generate_question(
                            "Factors, Multiples, LCM & HCF", "Challenge"
                        )
                        self.assertEqual(int(answer), math.lcm(a, b, c))
                        self.assertIn(f"{a}, {b} and {c}", question)
                        self.assertIn(f"LCM({a}, {b}) = {math.lcm(a, b)}", explanation)

    def test_existing_factor_questions_remain_available(self):
        for level in ("Easy", "Medium", "Challenge"):
            with patch.object(practice_generator, "_pick", return_value=True), patch.object(
                practice_generator, "_factors_roots", return_value=("existing",)
            ) as existing:
                self.assertEqual(
                    practice_generator.generate_question("Factors, Multiples, LCM & HCF", level),
                    ("existing",),
                )
                existing.assert_called_once_with(level)


if __name__ == "__main__":
    unittest.main()
