"""JSS3 binary subtraction uses two three-digit operands."""
import unittest
from unittest.mock import patch

import practice_generator


class BinarySubtractionTests(unittest.TestCase):
    def test_all_three_digit_subtraction_pairs(self):
        for a, b in ((5, 4), (6, 4), (6, 5), (7, 4), (7, 5), (7, 6)):
            with self.subTest(a=a, b=b), patch.object(
                practice_generator, "_pick", side_effect=[False, "subtract", (a, b)]
            ):
                question, hint, answer, explanation = practice_generator.generate_question("Number Bases", "Challenge")
                self.assertEqual(int(answer, 2), a - b)
                self.assertIn(f"{a:03b}₂ - {b:03b}₂", question)
                self.assertIn("base two", hint)
                self.assertIn(f"{a} - {b} = {a-b}", explanation)

    def test_all_two_digit_binary_products(self):
        for a in (2, 3):
            for b in (2, 3):
                with self.subTest(a=a, b=b), patch.object(
                    practice_generator, "_pick", side_effect=[False, "multiply"]
                ), patch.object(practice_generator, "_int", side_effect=[a, b]):
                    question, hint, answer, explanation = practice_generator.generate_question("Number Bases", "Challenge")
                    self.assertEqual(int(answer, 2), a * b)
                    self.assertIn(f"{a:02b}₂ × {b:02b}₂", question)
                    self.assertIn("Multiply in base two", hint)
                    self.assertIn(f"{a} × {b} = {a*b}", explanation)

    def test_exact_binary_division_and_multiplication_check(self):
        for dividend, divisor in ((4, 2), (4, 4), (5, 5), (6, 2), (6, 3), (6, 6), (7, 7)):
            with self.subTest(dividend=dividend, divisor=divisor), patch.object(
                practice_generator, "_pick", side_effect=[False, "divide", (dividend, divisor)]
            ):
                question, hint, answer, explanation = practice_generator.generate_question("Number Bases", "Challenge")
                quotient = int(answer, 2)
                self.assertEqual(quotient * divisor, dividend)
                self.assertIn(f"{dividend:b}₂ ÷ {divisor:b}₂", question)
                self.assertIn("Divide in base two", hint)
                self.assertIn(f"Check: {quotient} × {divisor} = {dividend}", explanation)

    def test_existing_number_base_paths_are_retained(self):
        for topic, level in (("Number Bases", "Easy"), ("Number Bases", "Medium"),
                             ("Number Bases", "Challenge"), ("Number Bases (Binary)", "Challenge")):
            with patch.object(practice_generator, "_pick", return_value=True), patch.object(
                practice_generator, "_number_bases", return_value=("existing",)
            ) as existing:
                self.assertEqual(practice_generator.generate_question(topic, level), ("existing",))
                existing.assert_called_once_with(level)


if __name__ == "__main__":
    unittest.main()
