"""JSS2 polygon practice covers the exterior-angle rule with exact answers."""
import unittest
from unittest.mock import patch

import practice_generator


class PolygonPracticeTests(unittest.TestCase):
    def test_regular_polygon_exterior_angles_have_exact_solutions(self):
        for sides in (3, 4, 5, 6, 8, 9, 10, 12, 15, 18, 20, 24, 30, 36):
            with self.subTest(sides=sides), patch.object(
                practice_generator, "_pick", side_effect=[False, sides]
            ):
                question, hint, answer, explanation = practice_generator.generate_question(
                    "Angles & Polygons", "Challenge"
                )
                angle = 360 // sides
                self.assertIn(f"{angle}°", question)
                self.assertIn("regular polygon", question)
                self.assertEqual(int(answer) * angle, 360)
                self.assertIn("360°", hint)
                self.assertIn(f"360 ÷ {angle} = {sides}", explanation)

    def test_existing_angle_questions_remain_available(self):
        for difficulty in ("Easy", "Medium", "Challenge"):
            with self.subTest(difficulty=difficulty), patch.object(
                practice_generator, "_pick", return_value=True
            ), patch.object(practice_generator, "_angles", return_value=("existing",)) as angles:
                result = practice_generator.generate_question("Angles & Polygons", difficulty)
                self.assertEqual(result, ("existing",))
                angles.assert_called_once_with(difficulty)


if __name__ == "__main__":
    unittest.main()
