"""Large-number practice includes millions, billions and trillions."""
import unittest
from unittest.mock import patch

import practice_generator


class LargeWholeNumbersTests(unittest.TestCase):
    def test_large_number_place_values(self):
        for name, unit in (("million", 10**6), ("billion", 10**9), ("trillion", 10**12)):
            for count in range(12, 100):
                with self.subTest(name=name, count=count), patch.object(
                    practice_generator, "_pick", side_effect=[True, (name, unit)]
                ), patch.object(practice_generator, "_int", return_value=count):
                    question, hint, answer, explanation = practice_generator.generate_question(
                        "Whole Numbers", "Challenge"
                    )
                    self.assertEqual(int(answer), count * unit)
                    self.assertIn(f"{count} {name}", question)
                    self.assertIn(f"{unit:,}", hint)
                    self.assertIn(f"{count * unit:,}", explanation)

    def test_existing_order_of_operations_remains_available(self):
        with patch.object(practice_generator, "_pick", return_value=False), patch.object(
            practice_generator, "_int", side_effect=[12, 3, 10]
        ):
            question, _, answer, _ = practice_generator.generate_question("Whole Numbers", "Challenge")
            self.assertEqual(question, "Calculate (12 × 3) - 10.")
            self.assertEqual(answer, "26")


if __name__ == "__main__":
    unittest.main()
