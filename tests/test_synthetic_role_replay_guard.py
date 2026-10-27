import os
import sqlite3
import tempfile
import unittest
from integration_research.synthetic_role_verifier import issue_synthetic_role,SyntheticRoleVerifier
from integration_research.role_replay_guard import SyntheticRoleReplayGuard

KEY=b"synthetic-only-role-replay-test-secret-12345678"

class RoleReplayTests(unittest.TestCase):
    def test_replay_rejected_even_after_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path=os.path.join(directory,"test.db")
            proof=issue_synthetic_role(actor="operator-A",role="operator",secret=KEY,expires=200)
            verifier=SyntheticRoleVerifier(secret=KEY,role="operator",actors={"operator-A"},clock=lambda:100)
            db=sqlite3.connect(path)
            guard=SyntheticRoleReplayGuard(db)
            self.assertEqual(guard.verify_once(verifier,proof),"operator-A")
            self.assertIsNone(guard.verify_once(verifier,proof))
            db.close()
            db=sqlite3.connect(path)
            self.assertIsNone(SyntheticRoleReplayGuard(db).verify_once(verifier,proof))
            db.close()
    def test_invalid_signature_does_not_redeem(self):
        db=sqlite3.connect(":memory:")
        try:
            guard=SyntheticRoleReplayGuard(db)
            verifier=SyntheticRoleVerifier(secret=KEY,role="reviewer",actors={"reviewer-A"},clock=lambda:100)
            proof=issue_synthetic_role(actor="reviewer-A",role="reviewer",secret=KEY,expires=200)
            self.assertIsNone(guard.verify_once(verifier,proof+"tampered"))
            self.assertEqual(guard.verify_once(verifier,proof),"reviewer-A")
        finally:
            db.close()

if __name__=="__main__":
    unittest.main()
