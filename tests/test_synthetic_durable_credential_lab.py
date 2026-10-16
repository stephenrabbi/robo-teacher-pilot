import os
import sqlite3
import tempfile
import unittest
from integration_research.durable_credential_lab import SyntheticDurableCredentialLab
from integration_research.provisioning_gate import ProvisioningDecision

class DurableSyntheticCredentialTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=os.path.join(self.temp.name,"synthetic.db")
        self.conn=sqlite3.connect(self.path)
        self.lab=SyntheticDurableCredentialLab(self.conn)
        self.decision=ProvisioningDecision("learner-A","school-A","synthetic-operator",True)
        self.password="synthetic-long-credential-123"
    def tearDown(self):
        self.conn.close()
        self.temp.cleanup()
    def test_restart_revocation_and_scope(self):
        self.lab.activate(decision=self.decision,password=self.password)
        session=self.lab.login(school_ref="school-A",learner_ref="learner-A",password=self.password)
        self.assertTrue(self.lab.verify_epoch(school_ref="school-A",learner_ref="learner-A",epoch=session["session_epoch"]))
        self.conn.close()
        self.conn=sqlite3.connect(self.path)
        self.lab=SyntheticDurableCredentialLab(self.conn)
        self.assertTrue(self.lab.verify_epoch(school_ref="school-A",learner_ref="learner-A",epoch=0))
        self.assertEqual(self.lab.revoke_all(school_ref="school-A",learner_ref="learner-A"),1)
        with self.assertRaises(PermissionError):
            self.lab.verify_epoch(school_ref="school-A",learner_ref="learner-A",epoch=0)
        with self.assertRaises(PermissionError):
            self.lab.login(school_ref="school-B",learner_ref="learner-A",password=self.password)
        self.assertTrue(self.lab.verify_epoch(school_ref="school-A",learner_ref="learner-A",epoch=1))
    def test_lockout_survives_restart(self):
        self.lab.activate(decision=self.decision,password=self.password)
        for _ in range(5):
            with self.assertRaises(PermissionError):
                self.lab.login(school_ref="school-A",learner_ref="learner-A",password="incorrect-but-long-password")
        self.conn.close()
        self.conn=sqlite3.connect(self.path)
        self.lab=SyntheticDurableCredentialLab(self.conn)
        with self.assertRaises(PermissionError):
            self.lab.login(school_ref="school-A",learner_ref="learner-A",password=self.password)
        with self.assertRaises(PermissionError):
            self.lab.verify_epoch(school_ref="school-A",learner_ref="learner-A",epoch=0)
    def test_rejects_unapproved_and_duplicate(self):
        with self.assertRaises(PermissionError):
            self.lab.activate(decision=ProvisioningDecision("learner-A","school-A","op",False),password=self.password)
        self.lab.activate(decision=self.decision,password=self.password)
        with self.assertRaises(PermissionError):
            self.lab.activate(decision=self.decision,password=self.password)

if __name__=="__main__":
    unittest.main()
