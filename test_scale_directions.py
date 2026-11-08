import unittest
from unittest.mock import patch
import practice_generator as generator

class ScaleDirectionTests(unittest.TestCase):
    def test_both_directions_for_all_measurements(self):
        for scale in range(2, 11):
            for length in range(3, 21):
                for actual in (False, True):
                    with self.subTest(scale=scale, length=length, actual=actual), patch.object(generator, "_int", side_effect=[scale, length]), patch.object(generator, "_pick", return_value=actual):
                        question, hint, answer, worked = generator.generate_question("Plane Shapes & Scale Drawing", "Challenge")
                        self.assertEqual(int(answer), scale*length if actual else length)
                        if actual:
                            self.assertIn("actual distance in km", question)
                            self.assertIn("Multiply", hint)
                            self.assertIn(f"{length} × {scale} = {length*scale}", worked)
                        else:
                            self.assertIn("on the map in cm", question)
                            self.assertIn("Divide", hint)
                            self.assertIn(f"{length*scale} ÷ {scale} = {length}", worked)
