import unittest
from unittest.mock import patch
import practice_generator as generator

class MeanWorkedAdditionTests(unittest.TestCase):
    def test_all_generated_means_show_sum_and_divisor(self):
        for middle in range(4, 21):
            for gap in range(1, 6):
                with self.subTest(middle=middle, gap=gap), patch.object(generator, "_int", side_effect=[middle, gap]):
                    question, _, answer, worked = generator.generate_question("Mean, Median & Mode", "Easy")
                    values = [middle-gap, middle, middle+gap]
                    self.assertIn(f"{values[0]} + {values[1]} + {values[2]} = {sum(values)}", worked)
                    self.assertIn(f"{sum(values)} ÷ {len(values)} = {middle}", worked)
                    self.assertEqual(int(answer), sum(values)/len(values))
                    self.assertIn(f"{values[0]}, {values[1]} and {values[2]}", question)
