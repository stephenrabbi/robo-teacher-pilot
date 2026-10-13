import unittest
from concurrent.futures import ThreadPoolExecutor
from enrollment_challenge_test_store import TestOnlyEnrollmentChallenges, EnrollmentDenied


class TestChallenge(unittest.TestCase):
    def setUp(self):
        self.now=[1000]
        self.store=TestOnlyEnrollmentChallenges(clock=lambda: self.now[0], ttl_seconds=60)

    def test_issue_and_single_use(self):
        ticket=self.store.issue("user-a")
        self.assertTrue(self.store.consume(ticket,"user-a").startswith("CLOUD-"))
        with self.assertRaises(EnrollmentDenied): self.store.consume(ticket,"user-a")

    def test_cross_account_rejected_without_consuming(self):
        ticket=self.store.issue("user-a")
        with self.assertRaises(EnrollmentDenied): self.store.consume(ticket,"user-b")
        self.assertTrue(self.store.consume(ticket,"user-a").startswith("CLOUD-"))

    def test_expired_rejected(self):
        ticket=self.store.issue("user-a")
        self.now[0]+=60
        with self.assertRaises(EnrollmentDenied): self.store.consume(ticket,"user-a")

    def test_missing_auth_denied(self):
        with self.assertRaises(EnrollmentDenied): self.store.issue("")

    def test_concurrent_consumption_only_one_wins(self):
        ticket=self.store.issue("user-a")
        def try_once(_):
            try:
                self.store.consume(ticket,"user-a")
                return True
            except EnrollmentDenied:
                return False
        with ThreadPoolExecutor(max_workers=8) as ex:
            outcomes=list(ex.map(try_once,range(24)))
        self.assertEqual(outcomes.count(True),1)

if __name__=="__main__":
    unittest.main()
