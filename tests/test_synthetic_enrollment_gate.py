"""Authorization gate fixture tests; no real identity or consent is asserted."""
import unittest
from datetime import datetime, timedelta, timezone
from dataclasses import replace
from integration_research.enrollment_gate import SyntheticDecision, SyntheticEnrollmentGate

class GateTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,10,11,tzinfo=timezone.utc)
        self.gate=SyntheticEnrollmentGate(authorized_school_reviewers={"school-reviewer"},
            authorized_guardian_reviewers={"guardian-reviewer"})
        self.school=SyntheticDecision("synthetic-A","synthetic-school","school-reviewer",
            "school_eligibility",True,self.now+timedelta(days=1))
        self.guardian=SyntheticDecision("synthetic-A","synthetic-school","guardian-reviewer",
            "guardian_authorization",True,self.now+timedelta(days=1))
    def evaluate(self,school=None,guardian=None):
        return self.gate.evaluate(learner_ref="synthetic-A",school_ref="synthetic-school",
            school_decision=self.school if school is None else school,
            guardian_decision=self.guardian if guardian is None else guardian,now=self.now)
    def test_both_independent_decisions_required(self):
        self.assertTrue(self.evaluate())
        for kwargs in ({"school":False},{"guardian":False}):
            with self.assertRaises(PermissionError):
                self.evaluate(**kwargs)
    def test_rejects_wrong_scopes_and_reviewers(self):
        for altered in (replace(self.school,learner_ref="synthetic-B"),
                        replace(self.school,school_ref="wrong-school"),
                        replace(self.school,issuer_ref="unauthorized"),
                        replace(self.school,approved=False),
                        replace(self.school,expires_at=self.now)):
            with self.assertRaises(PermissionError):
                self.evaluate(school=altered)
        with self.assertRaises(PermissionError):
            self.evaluate(guardian=replace(self.guardian,issuer_ref="school-reviewer"))
    def test_fails_closed_without_authorities(self):
        with self.assertRaises(ValueError):
            SyntheticEnrollmentGate(authorized_school_reviewers=set(),
                authorized_guardian_reviewers={"guardian-reviewer"})

if __name__=="__main__":
    unittest.main()
