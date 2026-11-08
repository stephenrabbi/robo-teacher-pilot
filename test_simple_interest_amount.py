import unittest
from unittest.mock import patch
import practice_generator as generator

class SimpleInterestAmountTests(unittest.TestCase):
    def test_interest_and_total_amount(self):
        for units in range(10, 51):
            for rate in (5, 8, 10, 12):
                for years in range(1, 5):
                    for total in (False, True):
                        with self.subTest(units=units, rate=rate, years=years, total=total), patch.object(generator, "_int", side_effect=[units, years]), patch.object(generator, "_pick", side_effect=[rate, total]):
                            question, _, answer, worked = generator.generate_question("Commercial Arithmetic", "Medium")
                            principal = units*1000
                            interest = principal*rate*years//100
                            self.assertEqual(int(answer), principal+interest if total else interest)
                            if total:
                                self.assertIn("principal plus interest", question)
                                self.assertIn(f"₦{principal:,} + ₦{interest:,} = ₦{principal+interest:,}", worked)
                            else:
                                self.assertIn("Find the simple interest", question)
