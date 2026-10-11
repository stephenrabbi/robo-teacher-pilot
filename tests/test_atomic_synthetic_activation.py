"""Synthetic transaction tests, not evidence of real guardian approval."""
import os
import sqlite3
import tempfile
import unittest
from integration_research.atomic_activation import AtomicSyntheticActivation

class AtomicTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=os.path.join(self.temp.name,"identity-test.sqlite")
        self.db=sqlite3.connect(self.path,isolation_level=None)
        self.verifier=lambda proof,school,learner: proof=="signed-test-A" and school=="school-A" and learner=="learner-A"
        self.service=AtomicSyntheticActivation(self.db,self.verifier)
    def tearDown(self):
        self.db.close()
        self.temp.cleanup()
    def test_valid_and_replay_rejection_restart(self):
        self.assertTrue(self.service.activate(school="school-A",learner="learner-A",approval_proof="signed-test-A"))
        self.db.close()
        self.db=sqlite3.connect(self.path,isolation_level=None)
        self.service=AtomicSyntheticActivation(self.db,self.verifier)
        with self.assertRaises(PermissionError):
            self.service.activate(school="school-A",learner="learner-A",approval_proof="signed-test-A")
        self.assertEqual(self.db.execute("SELECT count(*) FROM atomic_test_accounts").fetchone()[0],1)
    def test_wrong_scope_or_forged_proof_cannot_activate(self):
        for school,learner,proof in [("school-B","learner-A","signed-test-A"),
                                     ("school-A","learner-B","signed-test-A"),
                                     ("school-A","learner-A","forged")]:
            with self.assertRaises(PermissionError):
                self.service.activate(school=school,learner=learner,approval_proof=proof)
        self.assertEqual(self.db.execute("SELECT count(*) FROM atomic_test_accounts").fetchone()[0],0)
        self.assertEqual(self.db.execute("SELECT count(*) FROM atomic_test_approvals").fetchone()[0],0)
    def test_account_insert_failure_rolls_back_redemption(self):
        self.db.execute("""CREATE TRIGGER block_test_account BEFORE INSERT ON atomic_test_accounts
            BEGIN SELECT RAISE(ABORT,'synthetic failure'); END""")
        with self.assertRaises(sqlite3.IntegrityError):
            self.service.activate(school="school-A",learner="learner-A",approval_proof="signed-test-A")
        self.assertEqual(self.db.execute("SELECT count(*) FROM atomic_test_approvals").fetchone()[0],0)
        self.db.execute("DROP TRIGGER block_test_account")
        self.assertTrue(self.service.activate(school="school-A",learner="learner-A",approval_proof="signed-test-A"))

if __name__=="__main__":
    unittest.main()
