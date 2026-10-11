"""One synthetic authorization journey; no live routes, learners or deployment."""
import sqlite3
import unittest
from datetime import datetime,timedelta,timezone
from dataclasses import replace
from integration_research.enrollment_gate import SyntheticDecision,SyntheticEnrollmentGate
from integration_research.provisioning_gate import SyntheticProvisioningGate
from integration_research.durable_credential_lab import SyntheticDurableCredentialLab
from integration_research.recovery_gate import SyntheticRecoveryGate,RecoveryApproval
from integration_research.synthetic_role_verifier import SyntheticRoleVerifier,issue_synthetic_role
from integration_research.role_replay_guard import SyntheticRoleReplayGuard

KEY=b"isolated-synthetic-integration-key-12345678"

class JourneyTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(":memory:")
        self.now=datetime(2026,10,11,tzinfo=timezone.utc)
        self.events=[]
        self.replay=SyntheticRoleReplayGuard(self.db)
        self.verifier=SyntheticRoleVerifier(secret=KEY,role="operator",actors={"operator-A"},clock=lambda:100)
        self.verify_once=lambda proof:self.replay.verify_once(self.verifier,proof)
        self.enroll=SyntheticEnrollmentGate(authorized_school_reviewers={"school-reviewer"},
            authorized_guardian_reviewers={"guardian-reviewer"})
        self.provision=SyntheticProvisioningGate(enrollment_gate=self.enroll,
            verify_operator=self.verify_once,audit_sink=self.events.append)
        self.recovery=SyntheticRecoveryGate(reviewers={"recovery-reviewer"},
            verify_operator=self.verify_once,audit_sink=self.events.append)
        self.credentials=SyntheticDurableCredentialLab(self.db)
        self.school=SyntheticDecision("learner-A","school-A","school-reviewer",
            "school_eligibility",True,self.now+timedelta(days=1))
        self.guardian=SyntheticDecision("learner-A","school-A","guardian-reviewer",
            "guardian_authorization",True,self.now+timedelta(days=1))
    def tearDown(self):
        self.db.close()
    def proof(self,expires=200):
        return issue_synthetic_role(actor="operator-A",role="operator",
            secret=KEY,expires=expires)
    def authorize(self,proof,**kwargs):
        args=dict(learner_ref="learner-A",school_ref="school-A",
            school_decision=self.school,guardian_decision=self.guardian,
            operator_proof=proof,now=self.now)
        args.update(kwargs)
        return self.provision.authorize(**args)
    def test_authorized_activation_and_single_use_role(self):
        proof=self.proof()
        decision=self.authorize(proof)
        self.credentials.activate(decision=decision,password="synthetic-password-for-tests")
        self.assertEqual(self.credentials.login(school_ref="school-A",learner_ref="learner-A",
            password="synthetic-password-for-tests")["session_epoch"],0)
        with self.assertRaises(PermissionError):
            self.authorize(proof)
        with self.assertRaises(PermissionError):
            self.credentials.login(school_ref="school-B",learner_ref="learner-A",
                password="synthetic-password-for-tests")
    def test_denied_enrollment_does_not_consume_operator_proof(self):
        proof=self.proof()
        with self.assertRaises(PermissionError):
            self.authorize(proof,guardian_decision=replace(self.guardian,approved=False))
        self.assertTrue(self.authorize(proof).allowed)
    def test_recovery_rejects_proof_reuse_and_revokes_old_epoch(self):
        self.credentials.activate(decision=self.authorize(self.proof()),
            password="initial-synthetic-password")
        # Issue another time-scoped signed fixture; the first role assertion is consumed.
        recovery_proof=self.proof(expires=201)
        approval=RecoveryApproval("learner-A","school-A","recovery-reviewer",
            self.now+timedelta(days=1),True,"synthetic-recovery-decision-01")
        self.assertEqual(self.credentials.recover(recovery_gate=self.recovery,approval=approval,
            operator_proof=recovery_proof,new_password="replacement-synthetic-password",now=self.now),1)
        with self.assertRaises(PermissionError):
            self.credentials.verify_epoch(school_ref="school-A",learner_ref="learner-A",epoch=0)
        with self.assertRaises(PermissionError):
            self.credentials.recover(recovery_gate=self.recovery,approval=approval,
                operator_proof=recovery_proof,new_password="another-synthetic-password",now=self.now)
        self.assertEqual(self.credentials.login(school_ref="school-A",learner_ref="learner-A",
            password="replacement-synthetic-password")["session_epoch"],1)

if __name__=="__main__":
    unittest.main()
