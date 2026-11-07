"""Generated mode data must agree with the frequency stated in feedback."""
from collections import Counter
import re
import unittest
from unittest.mock import patch

import practice_generator


class ModeFeedbackTests(unittest.TestCase):
    def test_distractors_cannot_increase_the_intended_mode_frequency(self):
        for mode in range(2, 16):
            def choose_integer(low, high):
                # Also force the old distractor range to collide with the mode.
                if (low, high) in {(2, 15), (1, 20)}:
                    return mode
                return low

            with self.subTest(mode=mode), patch.object(
                practice_generator, "_int", side_effect=choose_integer
            ), patch.object(practice_generator, "_pick", side_effect=lambda values: next(iter(values))):
                question, _, answer, explanation = practice_generator.generate_question(
                    "Mean, Median & Mode", "Challenge"
                )
                values = list(map(int, re.findall(r"\d+", question)))
                frequencies = Counter(values)
                self.assertEqual(int(answer), mode)
                self.assertEqual(frequencies[mode], 3)
                self.assertEqual(frequencies.most_common(1), [(mode, 3)])
                self.assertIn(f"{mode} occurs three times", explanation)


if __name__ == "__main__":
    unittest.main()
