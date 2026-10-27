"""Synthetic provisioning authorization tests; no real credentials generated."""
import unittest
from datetime import datetime, timedelta, timezone
from dataclasses import replace
from integration_research.enrollment_gate import SyntheticDecision, SyntheticEnrollmentGate
from integration_research.provisioning_gate import SyntheticProvisioningGate

class ProvisioningTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,10,11,tzinfo=timezone.utc)
        self.school=SyntheticDecision("synthetic-A","synthetic-school","school-reviewer",
            "school_eligibility",True,self.now+timedelta(days=1))
        self.guardian=SyntheticDecision("synthetic-A","synthetic-school","guardian-reviewer",
            "guardian_authorization",True,self.now+timedelta(days=1))
        self.audit=[]
        enrollment=SyntheticEnrollmentGate(authorized_school_reviewers={"school-reviewer"},
            authorized_guardian_reviewers={"guardian-reviewer"})
        self.gate=SyntheticProvisioningGate(enrollment_gate=enrollment,
            verify_operator=lambda proof: "technical-operator" if proof=="fixture-authorized" else None,
            audit_sink=self.audit.append)
    def request(self, **changes):
        data=dict(learner_ref="synthetic-A",school_ref="synthetic-school",
            school_decision=self.school,guardian_decision=self.guardian,
            operator_proof="fixture-authorized",now=self.now)
        data.update(changes)
        return self.gate.authorize(**data)
    def test_independent_operator_and_both_approvals(self):
        decision=self.request()
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.operator_ref,"technical-operator")
        self.assertEqual(self.audit[-1]["allowed"],True)
        self.assertNotIn("operator_proof",self.audit[-1])
    def test_denies_missing_or_invalid_proof_and_approvals(self):
        for invalid in (
            {"operator_proof":None}, {"operator_proof":True},
            {"operator_proof":"unauthorized"},
            {"school_decision":replace(self.school,approved=False)},
            {"guardian_decision":replace(self.guardian,school_ref="different")},
            {"school_decision":replace(self.school,expires_at=self.now)},
        ):
            with self.subTest(invalid=invalid),self.assertRaises(PermissionError):
                self.request(**invalid)
            self.assertFalse(self.audit[-1]["allowed"])
    def test_different_approval_issuer_cannot_be_operator(self):
        enrollment=self.gate.enrollment_gate
        gate=SyntheticProvisioningGate(enrollment_gate=enrollment,
            verify_operator=lambda proof: "school-reviewer",audit_sink=self.audit.append)
        with self.assertRaises(PermissionError):
            gate.authorize(learner_ref="synthetic-A",school_ref="synthetic-school",
                school_decision=self.school,guardian_decision=self.guardian,
                operator_proof="fixture",now=self.now)
    def test_audit_failure_fails_closed(self):
        gate=SyntheticProvisioningGate(enrollment_gate=self.gate.enrollment_gate,
            verify_operator=lambda proof:"operator",audit_sink=lambda entry: (_ for _ in ()).throw(OSError("audit offline")))
        with self.assertRaises(OSError):
            gate.authorize(learner_ref="synthetic-A",school_ref="synthetic-school",
                school_decision=self.school,guardian_decision=self.guardian,
                operator_proof="fixture",now=self.now)
    def test_requires_independent_verifier(self):
        with self.assertRaises(ValueError):
            SyntheticProvisioningGate(enrollment_gate=self.gate.enrollment_gate,
                verify_operator=None,audit_sink=self.audit.append)

if __name__=="__main__":
    unittest.main()
