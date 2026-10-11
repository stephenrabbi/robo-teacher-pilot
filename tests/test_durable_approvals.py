import os
import sqlite3
import tempfile
import unittest
from progress_store.durable_approvals import DurableApprovalGate, create_approval_schema
from progress_store.enrollment_gateway import VerifiedEnrollmentGateway
from progress_store.signed_approval_provider import SignedApprovalVerifier, sign_synthetic_approval

KEY=b"synthetic-school-provider-key-1234567890"
SESSION_KEY=b"synthetic-session-key-for-gateway-1234567890"

def assertion(decision_id, *, kind="enrollment", subject="learner1", school="school1", reviewer="teacher1"):
    return sign_synthetic_approval(dict(
        issuer="school-provider",decision_id=decision_id,subject=subject,school=school,
        reviewer_id=reviewer,kind=kind,approved=True,issued_at=1000,expires_at=1100
    ),secret=KEY)

class DurableApprovalTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=os.path.join(self.temp.name,"replay.sqlite")
        self.db=sqlite3.connect(self.path,timeout=5)
        create_approval_schema(self.db)
        self.gateway=VerifiedEnrollmentGateway(SESSION_KEY,{"teacher1"})
        self.verifier=SignedApprovalVerifier(provider_id="school-provider",secret=KEY,clock=lambda:1050)
        self.gate=DurableApprovalGate(self.db,self.verifier.verify,self.gateway,provider_id="school-provider")
    def tearDown(self):
        self.db.close()
        self.temp.cleanup()
    def test_enrollment_is_single_use_after_restart(self):
        claim=assertion("enroll-1")
        self.assertTrue(self.gate.enroll(claim,school="school1",subject="learner1"))
        self.db.close()
        self.db=sqlite3.connect(self.path)
        other=DurableApprovalGate(self.db,self.verifier.verify,self.gateway,provider_id="school-provider")
        with self.assertRaises(PermissionError):
            other.enroll(claim,school="school1",subject="learner1")
    def test_denied_reviewer_does_not_consume_approval(self):
        claim=assertion("wrong-reviewer",reviewer="stranger")
        with self.assertRaises(PermissionError):
            self.gate.enroll(claim,school="school1",subject="learner1")
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM redeemed_approvals").fetchone()[0],0)
    def test_tampered_scope_does_not_consume_approval(self):
        claim=assertion("scope-1")
        with self.assertRaises(PermissionError):
            self.gate.enroll(claim,school="other",subject="learner1")
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM redeemed_approvals").fetchone()[0],0)
    def test_recovery_requires_enrollment_and_distinct_approval(self):
        proof=assertion("recover-1",kind="recovery")
        with self.assertRaises(PermissionError):
            self.gate.authorize_recovery(proof,school="school1",subject="learner1")
        self.gate.enroll(assertion("enroll-1"),school="school1",subject="learner1")
        self.assertTrue(self.gate.authorize_recovery(proof,school="school1",subject="learner1"))
        with self.assertRaises(PermissionError):
            self.gate.authorize_recovery(proof,school="school1",subject="learner1")
    def test_same_decision_cannot_be_reused_for_other_kind(self):
        self.gate.enroll(assertion("same-ref"),school="school1",subject="learner1")
        with self.assertRaises(PermissionError):
            self.gate.authorize_recovery(assertion("same-ref",kind="recovery"),school="school1",subject="learner1")

if __name__=="__main__":
    unittest.main()
