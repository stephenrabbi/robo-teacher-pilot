import unittest
from integration_research.synthetic_role_verifier import SyntheticRoleVerifier, issue_synthetic_role

KEY=b"synthetic-role-verifier-test-secret-1234567890"
OTHER=b"other-issuer-test-signing-secret-1234567890"
class RoleTests(unittest.TestCase):
    def test_verified_operator_and_reviewer_separation(self):
        op=SyntheticRoleVerifier(secret=KEY,role="operator",actors={"op-A"},clock=lambda:100)
        reviewer=SyntheticRoleVerifier(secret=KEY,role="reviewer",actors={"review-A"},clock=lambda:100)
        operator=issue_synthetic_role(actor="op-A",role="operator",secret=KEY,expires=200)
        review=issue_synthetic_role(actor="review-A",role="reviewer",secret=KEY,expires=200)
        self.assertEqual(op(operator),"op-A")
        self.assertEqual(reviewer(review),"review-A")
        self.assertIsNone(op(review))
        self.assertIsNone(reviewer(operator))
    def test_invalid_expired_wrong_issuer_and_unauthorized(self):
        verifier=SyntheticRoleVerifier(secret=KEY,role="operator",actors={"op-A"},clock=lambda:100)
        samples=[
            issue_synthetic_role(actor="op-A",role="operator",secret=KEY,expires=100),
            issue_synthetic_role(actor="op-A",role="operator",secret=OTHER,expires=200),
            issue_synthetic_role(actor="op-B",role="operator",secret=KEY,expires=200),
            issue_synthetic_role(actor="op-A",role="operator",secret=KEY,expires=200,issuer="other"),
            "untrusted",True,None,
        ]
        for item in samples:
            with self.subTest(item=item):
                self.assertIsNone(verifier(item))
    def test_missing_allowlist_fails_closed(self):
        with self.assertRaises(ValueError):
            SyntheticRoleVerifier(secret=KEY,role="operator",actors=set())
if __name__=="__main__":
    unittest.main()
