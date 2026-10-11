import unittest
from progress_store.approval_evidence import EvidenceGatedIdentity, VerifiedDecision
from progress_store.enrollment_gateway import VerifiedEnrollmentGateway

KEY=b"synthetic-provider-validation-key-1234567890"

class ApprovalEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.gateway=VerifiedEnrollmentGateway(KEY, {"school-reviewer"})
        self.decisions={
            "enroll-1":VerifiedDecision("enroll-1","A","school-one","school-reviewer","enrollment",True),
            "recovery-1":VerifiedDecision("recovery-1","A","school-one","school-reviewer","recovery",True),
            "denied":VerifiedDecision("denied","B","school-one","school-reviewer","enrollment",False),
        }
        self.gate=EvidenceGatedIdentity(self.gateway,self.decisions.get)

    def test_missing_provider_denied(self):
        with self.assertRaises(ValueError):
            EvidenceGatedIdentity(self.gateway,None)
        with self.assertRaises(PermissionError):
            self.gate.enroll(reference="unknown",subject="A",school="school-one")

    def test_verified_enrollment_issues_scoped_session(self):
        self.gate.enroll(reference="enroll-1",subject="A",school="school-one")
        self.assertTrue(self.gateway.issue(subject="A",school="school-one",now=1000))
        with self.assertRaises(PermissionError):
            self.gateway.issue(subject="B",school="school-one",now=1000)

    def test_wrong_school_or_learner_denied(self):
        for subject, school in (("B","school-one"),("A","school-two")):
            with self.assertRaises(PermissionError):
                self.gate.enroll(reference="enroll-1",subject=subject,school=school)

    def test_denied_decision_and_replay_denied(self):
        with self.assertRaises(PermissionError):
            self.gate.enroll(reference="denied",subject="B",school="school-one")
        self.gate.enroll(reference="enroll-1",subject="A",school="school-one")
        with self.assertRaises(PermissionError):
            self.gate.enroll(reference="enroll-1",subject="A",school="school-one")

    def test_recovery_needs_separate_proof_and_existing_enrollment(self):
        with self.assertRaises(PermissionError):
            self.gate.authorize_recovery(reference="recovery-1",subject="A",school="school-one")
        self.gate.enroll(reference="enroll-1",subject="A",school="school-one")
        with self.assertRaises(PermissionError):
            self.gate.authorize_recovery(reference="enroll-1",subject="A",school="school-one")
        self.assertTrue(self.gate.authorize_recovery(reference="recovery-1",subject="A",school="school-one"))
        with self.assertRaises(PermissionError):
            self.gate.authorize_recovery(reference="recovery-1",subject="A",school="school-one")

if __name__=="__main__":
    unittest.main()
