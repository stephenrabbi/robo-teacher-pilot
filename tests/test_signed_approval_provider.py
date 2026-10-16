import unittest
from progress_store.signed_approval_provider import SignedApprovalVerifier, sign_synthetic_approval

KEY=b"trusted-provider-test-key-0123456789-abcdef"
def claims(**overrides):
    data=dict(issuer="school-provider",decision_id="unique-123",subject="learner-A",
        school="school-X",reviewer_id="school-reviewer",kind="enrollment",
        approved=True,issued_at=1000,expires_at=1100)
    data.update(overrides)
    return data

class SignedProviderTests(unittest.TestCase):
    def setUp(self):
        self.verifier=SignedApprovalVerifier(provider_id="school-provider",secret=KEY,clock=lambda:1050)
    def token(self, **kw):
        return sign_synthetic_approval(claims(**kw),secret=KEY)
    def test_valid_approval(self):
        decision=self.verifier.verify(self.token())
        self.assertEqual((decision.subject,decision.school,decision.kind),("learner-A","school-X","enrollment"))
    def test_tampered_and_untrusted_signatures_rejected(self):
        token=self.token()
        body,mac=token.split(".")
        for untrusted in (body+"."+mac[:-2]+"AA",sign_synthetic_approval(claims(),secret=b"other-provider-key-01234567890123456789")):
            with self.assertRaises(PermissionError):
                self.verifier.verify(untrusted)
    def test_other_issuer_and_denied_rejected(self):
        for data in (dict(issuer="other"),dict(approved=False)):
            with self.assertRaises(PermissionError):
                self.verifier.verify(self.token(**data))
    def test_expired_future_and_long_lived_rejected(self):
        for data in (dict(expires_at=1050),dict(issued_at=1051),dict(expires_at=1800)):
            with self.assertRaises(PermissionError):
                self.verifier.verify(self.token(**data))
    def test_wrong_types_and_unexpected_claims_rejected(self):
        for data in (dict(issued_at=True),dict(subject=""),dict(kind="admin"),dict(approved="true")):
            with self.assertRaises(PermissionError):
                self.verifier.verify(self.token(**data))
    def test_invalid_format_rejected(self):
        for token in ("", "garbage", "invalid.invalid.invalid"):
            with self.assertRaises(PermissionError):
                self.verifier.verify(token)

if __name__=="__main__":
    unittest.main()
