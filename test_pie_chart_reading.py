import unittest
from unittest.mock import patch
from fractions import Fraction
import practice_generator as generator

class PieChartReadingTests(unittest.TestCase):
    def test_all_generated_sector_counts(self):
        for total in (20, 24, 30, 36, 40, 45, 60):
            for count in range(1, total):
                with self.subTest(total=total, count=count), patch.object(generator, "_pick", return_value=total), patch.object(generator, "_int", return_value=count):
                    question, hint, answer, worked = generator.generate_question("Pie Charts", "Challenge")
                    angle = Fraction(count * 360, total)
                    self.assertIn(f"sector is {generator._fraction(angle)}°", question)
                    self.assertEqual(int(answer), count)
                    self.assertEqual(angle / 360 * total, count)
                    self.assertIn(f"{count} learners chose football", worked)
                    self.assertIn("360", hint)

    def test_lower_levels_still_ask_for_angle(self):
        for level in ("Easy", "Medium"):
            with patch.object(generator, "_pick", return_value=20), patch.object(generator, "_int", return_value=5):
                question, _, answer, _ = generator.generate_question("Pie Charts", level)
                self.assertIn("Find the angle", question)
                self.assertEqual(answer, "90")
