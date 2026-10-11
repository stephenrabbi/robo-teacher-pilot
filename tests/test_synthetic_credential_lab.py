import unittest
from integration_research.credential_lab import SyntheticCredentialLab
from integration_research.provisioning_gate import ProvisioningDecision

class SyntheticCredentialTests(unittest.TestCase):
    def setUp(self):
        self.lab=SyntheticCredentialLab()
        self.valid=ProvisioningDecision("learner-A","school-A","operator-A",True)
        self.password="test-only-long-password-01"
    def test_activation_login_and_revocation_epoch(self):
        self.lab.activate(decision=self.valid,password=self.password)
        result=self.lab.login(school_ref="school-A",learner_ref="learner-A",password=self.password)
        self.assertEqual(result["session_epoch"],0)
        self.assertEqual(self.lab.revoke_all(school_ref="school-A",learner_ref="learner-A"),1)
        self.assertEqual(self.lab.login(school_ref="school-A",learner_ref="learner-A",password=self.password)["session_epoch"],1)
        with self.assertRaises(PermissionError):
            self.lab.activate(decision=self.valid,password=self.password)
    def test_rejects_unapproved_short_credentials_wrong_school(self):
        with self.assertRaises(PermissionError):
            self.lab.activate(decision=ProvisioningDecision("learner-A","school-A","op",False),password=self.password)
        with self.assertRaises(ValueError):
            self.lab.activate(decision=self.valid,password="short")
        self.lab.activate(decision=self.valid,password=self.password)
        with self.assertRaises(PermissionError):
            self.lab.login(school_ref="school-B",learner_ref="learner-A",password=self.password)
    def test_failed_attempts_lock_out(self):
        self.lab.activate(decision=self.valid,password=self.password)
        for i in range(5):
            with self.assertRaises(PermissionError):
                self.lab.login(school_ref="school-A",learner_ref="learner-A",password="not-the-password")
        with self.assertRaises(PermissionError):
            self.lab.login(school_ref="school-A",learner_ref="learner-A",password=self.password)
if __name__=="__main__":
    unittest.main()
