import sqlite3
import unittest
from datetime import datetime, timedelta, timezone
from dataclasses import replace
from integration_research.durable_credential_lab import SyntheticDurableCredentialLab
from integration_research.provisioning_gate import ProvisioningDecision
from integration_research.recovery_gate import SyntheticRecoveryGate, RecoveryApproval

class SyntheticRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(":memory:")
        self.lab=SyntheticDurableCredentialLab(self.db)
        self.lab.activate(decision=ProvisioningDecision("learner-A","school-A","operator",True),
                          password="original-synthetic-password")
        self.now=datetime(2026,10,11,tzinfo=timezone.utc)
        self.approval=RecoveryApproval("learner-A","school-A","school-recovery-reviewer",
            self.now+timedelta(days=1),True)
        self.audits=[]
        self.gate=SyntheticRecoveryGate(reviewers={"school-recovery-reviewer"},
            verify_operator=lambda proof:"different-operator" if proof=="approved-test-proof" else None,
            audit_sink=self.audits.append)
    def tearDown(self):
        self.db.close()
    def test_recovery_revokes_old_epoch_and_replaces_password(self):
        self.assertEqual(self.lab.recover(recovery_gate=self.gate,approval=self.approval,
            operator_proof="approved-test-proof",new_password="replacement-synthetic-password",now=self.now),1)
        with self.assertRaises(PermissionError):
            self.lab.verify_epoch(school_ref="school-A",learner_ref="learner-A",epoch=0)
        with self.assertRaises(PermissionError):
            self.lab.login(school_ref="school-A",learner_ref="learner-A",password="original-synthetic-password")
        self.assertEqual(self.lab.login(school_ref="school-A",learner_ref="learner-A",
            password="replacement-synthetic-password")["session_epoch"],1)
    def test_recovery_denies_invalid_authority(self):
        cases=[(replace(self.approval,approved=False),"approved-test-proof"),
               (replace(self.approval,school_ref="wrong-school"),"approved-test-proof"),
               (replace(self.approval,expires_at=self.now),"approved-test-proof"),
               (self.approval,None)]
        for approval,proof in cases:
            with self.subTest(approval=approval,proof=proof),self.assertRaises(PermissionError):
                self.lab.recover(recovery_gate=self.gate,approval=approval,
                    operator_proof=proof,new_password="replacement-synthetic-password",now=self.now)
        self.assertEqual(self.lab.login(school_ref="school-A",learner_ref="learner-A",
            password="original-synthetic-password")["session_epoch"],0)

if __name__=="__main__":
    unittest.main()
