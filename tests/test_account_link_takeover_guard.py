import unittest
from account_link_takeover_guard import Link, LinkConflict, TestLinkRegistry


class TestLinkSafety(unittest.TestCase):
    def setUp(self):
        self.reg=TestLinkRegistry()
        self.a=Link("WEB-A", "user-a")
        self.b=Link("WEB-B", "user-b")

    def test_two_distinct_accounts(self):
        self.assertEqual(self.reg.bind_verified(self.a), self.a)
        self.assertEqual(self.reg.bind_verified(self.b), self.b)

    def test_idempotent_rebind(self):
        self.reg.bind_verified(self.a)
        self.assertEqual(self.reg.bind_verified(self.a),self.a)

    def test_cannot_claim_another_account_classroom(self):
        self.reg.bind_verified(self.a)
        with self.assertRaises(LinkConflict):
            self.reg.bind_verified(Link("WEB-A","user-b"))

    def test_cannot_claim_another_classroom_with_existing_account(self):
        self.reg.bind_verified(self.a)
        with self.assertRaises(LinkConflict):
            self.reg.bind_verified(Link("WEB-B","user-a"))

    def test_reject_bad_classroom_identity(self):
        with self.assertRaises(ValueError):
            self.reg.bind_verified(Link("IND-ONLY","user-a"))


if __name__ == "__main__":
    unittest.main()
