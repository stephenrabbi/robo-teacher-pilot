"""JSS2 NERDC Bearing: bearings of A from B and B from A (printed p. 26)."""
import unittest
from unittest.mock import patch

import practice_generator as generator


class ReverseBearingTests(unittest.TestCase):
    def test_every_three_figure_bearing_and_worked_wrap(self):
        for bearing in range(360):
            with self.subTest(bearing=bearing), patch.object(generator, "_int", return_value=bearing):
                question, hint, answer, worked = generator.generate_question("Bearings & Distances", "Challenge")
                expected = (bearing + 180) % 360
                self.assertIn(f"bearing of B from A is {bearing:03d}°", question)
                self.assertIn("bearing of A from B", question)
                self.assertEqual(answer, f"{expected:03d}")
                self.assertIn(f"{bearing}° + 180° = {bearing + 180}°", worked)
                self.assertIn(f"bearing of A from B is {expected:03d}°", worked)
                self.assertEqual((int(answer) + 180) % 360, bearing)
                if bearing >= 180:
                    self.assertIn(f"{bearing + 180}° − 360° = {expected}°", worked)
                else:
                    self.assertIn("no full turn is removed", worked)

    def test_easy_and_medium_keep_clockwise_turns(self):
        for level in ("Easy", "Medium"):
            with patch.object(generator, "_int", return_value=35), patch.object(generator, "_pick", return_value=30):
                question, _, answer, _ = generator.generate_question("Bearings & Distances", level)
                self.assertIn("clockwise", question)
                self.assertEqual(answer, "020")


if __name__ == "__main__":
    unittest.main()
