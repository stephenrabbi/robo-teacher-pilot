import unittest
from fractions import Fraction
from unittest.mock import patch
import practice_generator as generator

class PieWorkedStepsTests(unittest.TestCase):
    def test_worked_fraction_and_angle_for_all_choices(self):
        for total in (20, 24, 30, 36, 40, 45, 60):
            for category in range(1, total):
                with self.subTest(total=total, category=category), patch.object(generator, "_pick", return_value=total), patch.object(generator, "_int", return_value=category):
                    _, _, answer, worked = generator.generate_question("Pie Charts", "Easy")
                    share = Fraction(category, total)
                    angle = share * 360
                    self.assertIn(f"{category}/{total} = {generator._fraction(share)}", worked)
                    self.assertIn(f"{generator._fraction(share)} × 360° = {generator._fraction(angle)}°", worked)
                    self.assertEqual(answer, generator._fraction(angle))
