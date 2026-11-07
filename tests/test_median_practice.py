"""Median practice orders the data before averaging the middle values."""
from fractions import Fraction
import re
import unittest
from unittest.mock import patch

import practice_generator


class MedianPracticeTests(unittest.TestCase):
    def test_reversed_data_uses_ordered_middle_values(self):
        for gap in (2, 3):
            with self.subTest(gap=gap), patch.object(
                practice_generator, "_int", side_effect=[8, gap, 15]
            ), patch.object(practice_generator.secrets, "SystemRandom") as random:
                random.return_value.shuffle.side_effect = lambda values: values.reverse()
                question, hint, answer, explanation = practice_generator.generate_question(
                    "Mean, Median & Mode", "Medium"
                )
                data = list(map(int, re.findall(r"-?\d+", question)))
                self.assertNotEqual(data, sorted(data))
                ordered = sorted(data)
                self.assertEqual(Fraction(answer), Fraction(ordered[1] + ordered[2], 2))
                self.assertIn(", ".join(map(str, ordered)), explanation)
                self.assertIn("Arrange the values", hint)


if __name__ == "__main__":
    unittest.main()
