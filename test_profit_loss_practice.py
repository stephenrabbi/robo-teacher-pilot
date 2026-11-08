import unittest
from unittest.mock import patch
import practice_generator as generator

class ProfitLossPracticeTests(unittest.TestCase):
    def test_all_costs_amounts_and_directions(self):
        for cost_factor in range(5, 31):
            for amount_factor in range(1, 11):
                for loss_case in (False, True):
                    with self.subTest(cost=cost_factor, amount=amount_factor, loss=loss_case), patch.object(generator, "_int", side_effect=[cost_factor, amount_factor]), patch.object(generator, "_pick", return_value=loss_case):
                        question, hint, answer, worked = generator.generate_question("Commercial Arithmetic", "Easy")
                        cost = cost_factor*100
                        amount = min(amount_factor*50, cost-50) if loss_case else amount_factor*50
                        selling = cost-amount if loss_case else cost+amount
                        self.assertGreater(selling, 0)
                        self.assertEqual(int(answer), abs(selling-cost))
                        self.assertIn(f"sells for ₦{selling:,}", question)
                        self.assertIn("Find the loss" if loss_case else "Find the profit", question)
                        self.assertIn(f"₦{amount:,}", worked)
                        if loss_case:
                            self.assertIn(f"₦{cost:,} − ₦{selling:,} = ₦{amount:,}", worked)
                            self.assertIn("Subtract selling price from cost price", hint)
