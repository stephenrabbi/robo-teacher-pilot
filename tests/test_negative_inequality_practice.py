"""Negative coefficient challenges reverse the inequality direction."""
import unittest
from unittest.mock import patch

import practice_generator


class NegativeInequalityTests(unittest.TestCase):
    def test_least_solution_and_reversed_direction(self):
        for solution in range(1, 13):
            for coefficient in range(2, 7):
                for constant in (1, 10):
                    with self.subTest(x=solution, coefficient=coefficient, constant=constant), patch.object(
                        practice_generator, "_pick", return_value=True
                    ), patch.object(practice_generator, "_int", side_effect=[solution, coefficient, constant]):
                        question, hint, answer, explanation = practice_generator.generate_question(
                            "Linear Inequalities", "Challenge"
                        )
                        bound = constant - coefficient * solution
                        x = int(answer)
                        self.assertLessEqual(-coefficient * x + constant, bound)
                        self.assertGreater(-coefficient * (x - 1) + constant, bound)
                        self.assertIn(f"≤ {bound}", question)
                        self.assertIn("reverse", hint)
                        self.assertIn(f"x ≥ {solution}", explanation)

    def test_positive_coefficient_challenge_is_retained(self):
        with patch.object(practice_generator, "_pick", return_value=False), patch.object(
            practice_generator, "_int", side_effect=[5, 3, 2]
        ):
            question, _, answer, _ = practice_generator.generate_question("Linear Inequalities", "Challenge")
            self.assertIn("3x - 2 ≥ 13", question)
            self.assertEqual(answer, "5")


if __name__ == "__main__":
    unittest.main()
