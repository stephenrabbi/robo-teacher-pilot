import unittest
from unittest.mock import patch

from progress_store.identity_prototype import TestIdentityAuthority
from progress_store.session_auth import verify_session

KEY = b"test-signing-key-for-synthetic-records-only-00001"

class TestIdentityIssuance(unittest.TestCase):
    def setUp(self):
        self.authority = TestIdentityAuthority(KEY)
        self.authority.register_approved(subject="synthetic-A", school="school-one", approved=True)

    def test_enrollment_alone_cannot_issue_session(self):
        self.assertFalse(hasattr(self.authority, "issue_for_approved"))
        self.assertIn(("school-one", "synthetic-A"), self.authority._enrollments)

    def test_no_recovery_without_separate_approval(self):
        with self.assertRaises(PermissionError):
            self.authority.create_recovery_challenge(subject="synthetic-A", school="school-one", approved_recovery=False, now=1000)

    def test_recovery_single_use_and_rejects_wrong_secret(self):
        challenge = self.authority.create_recovery_challenge(subject="synthetic-A", school="school-one", approved_recovery=True, now=1000)
        with self.assertRaises(PermissionError):
            self.authority.redeem_recovery(subject="synthetic-A", school="school-one", challenge="wrong", now=1001)
        with self.assertRaises(PermissionError):
            self.authority.redeem_recovery(subject="synthetic-A", school="school-one", challenge=challenge, now=1001)

    def test_recovery_success_and_cannot_replay(self):
        challenge = self.authority.create_recovery_challenge(subject="synthetic-A", school="school-one", approved_recovery=True, now=1000)
        token = self.authority.redeem_recovery(subject="synthetic-A", school="school-one", challenge=challenge, now=1001)
        self.assertTrue(verify_session(token, secret=KEY, now=1002).verified)
        with self.assertRaises(PermissionError):
            self.authority.redeem_recovery(subject="synthetic-A", school="school-one", challenge=challenge, now=1002)

    def test_expired_recovery_rejected(self):
        challenge = self.authority.create_recovery_challenge(subject="synthetic-A", school="school-one", approved_recovery=True, now=1000)
        with self.assertRaises(PermissionError):
            self.authority.redeem_recovery(subject="synthetic-A", school="school-one", challenge=challenge, now=1600)

if __name__ == "__main__":
    unittest.main()
