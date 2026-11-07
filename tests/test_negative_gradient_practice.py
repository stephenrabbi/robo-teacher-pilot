"""Linear graph practice includes falling lines and signed coordinate changes."""
from fractions import Fraction
import re
import unittest
from unittest.mock import patch

import practice_generator


class SignedGradientTests(unittest.TestCase):
    def test_gradient_matches_generated_coordinates_for_both_signs(self):
        for sign in (-1, 1):
            for magnitude in range(2, 7):
                for dx in range(2, 7):
                    for x1, y1 in ((0, 0), (5, 8)):
                        with patch.object(practice_generator, "_pick", return_value=sign), patch.object(
                            practice_generator, "_int", side_effect=[x1, y1, magnitude, dx]
                        ):
                            question, _, answer, explanation = practice_generator.generate_question("Linear Graphs", "Medium")
                            ax, ay, bx, by = map(int, re.findall(r"-?\d+", question))
                            self.assertEqual(Fraction(by - ay, bx - ax), int(answer))
                            self.assertEqual(int(answer), sign * magnitude)
                            self.assertIn(f"Change in y = {by - ay}", explanation)

    def test_missing_x_equations_keep_their_solution_for_both_signs(self):
        for sign in (-1, 1):
            for offset in (-8, 8):
                for solution in (2, 10):
                    with patch.object(practice_generator, "_pick", return_value=sign), patch.object(
                        practice_generator, "_int", side_effect=[0, 0, 3, 2, offset, solution]
                    ):
                        question, _, answer, _ = practice_generator.generate_question("Linear Graphs", "Challenge")
                        self.assertEqual(int(answer), solution)
                        self.assertIn(f"(x, {sign * 3 * solution + offset})", question)
                        self.assertIn(f"y = {sign * 3}x", question)


if __name__ == "__main__":
    unittest.main()
