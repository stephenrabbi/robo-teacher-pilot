"""Similar-shape challenges recover a smaller corresponding length."""
import unittest
from unittest.mock import patch

import practice_generator


class SimilarShapesPracticeTests(unittest.TestCase):
    def test_missing_smaller_side_for_every_generated_pair(self):
        for scale in range(2, 7):
            for side in range(2, 16):
                with self.subTest(scale=scale, side=side), patch.object(
                    practice_generator, "_int", side_effect=[scale, side]
                ):
                    question, hint, answer, explanation = practice_generator.generate_question(
                        "Similar Shapes", "Challenge"
                    )
                    self.assertEqual(int(answer) * scale, scale * side)
                    self.assertIn(f"larger shape is {scale}", question)
                    self.assertIn(f"{scale * side} cm", question)
                    self.assertIn("Divide", hint)
                    self.assertIn(f"{scale * side} ÷ {scale} = {side}", explanation)

    def test_scale_factor_questions_remain_at_other_difficulties(self):
        for level in ("Easy", "Medium"):
            with self.subTest(level=level), patch.object(
                practice_generator, "_int", side_effect=[3, 5]
            ):
                question, _, answer, _ = practice_generator.generate_question("Similar Shapes", level)
                self.assertIn("Find the scale factor from the smaller shape to the larger shape", question)
                self.assertEqual(answer, "3")


if __name__ == "__main__":
    unittest.main()
