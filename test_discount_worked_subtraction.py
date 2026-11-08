import unittest
from unittest.mock import patch
import practice_generator as generator

class DiscountWorkedSubtractionTests(unittest.TestCase):
    def test_all_generated_prices_and_discounts(self):
        for multiplier in range(10, 51):
            for discount in (10, 15, 20, 25):
                with self.subTest(multiplier=multiplier, discount=discount), patch.object(generator, "_int", side_effect=[10, 1, multiplier]), patch.object(generator, "_pick", side_effect=[5, discount]):
                    question, _, answer, worked = generator.generate_question("Commercial Arithmetic", "Challenge")
                    price = multiplier * 500
                    reduction = price * discount // 100
                    expected = price - reduction
                    self.assertEqual(int(answer), expected)
                    self.assertIn(f"₦{price:,} − ₦{reduction:,} = ₦{expected:,}", worked)
                    self.assertIn(f"{discount}% discount", question)
                    self.assertGreater(expected, 0)
                    self.assertLess(expected, price)
