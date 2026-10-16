import sqlite3
import unittest
from progress_store.durable_identity import create_identity_schema
from progress_store.proof_login import create_login_schema,SyntheticProofLogin
from progress_store.session_auth import verify_session

KEY=b"synthetic-proof-login-session-key-123456789"
PASSWORD="long-synthetic-test-credential-2026"

class ProofLoginTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(":memory:")
        create_identity_schema(self.db)
        create_login_schema(self.db)
        self.login=SyntheticProofLogin(self.db,signing_key=KEY,clock=lambda:1050)
        self.db.execute("INSERT INTO synthetic_enrollments (school,subject,reviewer_id,approved_at) VALUES (?,?,?,?)",
                        ("school-A","learner-A","trusted",1000))
        self.db.commit()
    def tearDown(self):
        self.db.close()
    def test_enrollment_without_login_proof_rejected(self):
        with self.assertRaises(PermissionError):
            self.login.login(school="school-A",subject="learner-A",credential=PASSWORD)
    def test_only_authorized_provisioning(self):
        with self.assertRaises(PermissionError):
            self.login.provision(school="school-A",subject="learner-A",credential=PASSWORD)
        with self.assertRaises(PermissionError):
            self.login.provision(school="school-A",subject="stranger",credential=PASSWORD,authorized_operator=True)
    def test_authenticated_login_scoped(self):
        self.login.provision(school="school-A",subject="learner-A",credential=PASSWORD,authorized_operator=True)
        token=self.login.login(school="school-A",subject="learner-A",credential=PASSWORD)
        principal=verify_session(token,secret=KEY,now=1050)
        self.assertEqual((principal.school,principal.subject),("school-A","learner-A"))
        with self.assertRaises(PermissionError):
            self.login.login(school="school-A",subject="learner-A",credential="wrong-synthetic-password-123")
        with self.assertRaises(PermissionError):
            self.login.login(school="school-B",subject="learner-A",credential=PASSWORD)
    def test_duplicate_provisioning_denied(self):
        self.login.provision(school="school-A",subject="learner-A",credential=PASSWORD,authorized_operator=True)
        with self.assertRaises(PermissionError):
            self.login.provision(school="school-A",subject="learner-A",credential=PASSWORD,authorized_operator=True)
    def test_revocation_disables_login(self):
        self.login.provision(school="school-A",subject="learner-A",credential=PASSWORD,authorized_operator=True)
        self.db.execute("DELETE FROM synthetic_enrollments WHERE school=? AND subject=?",("school-A","learner-A"))
        self.db.commit()
        with self.assertRaises(PermissionError):
            self.login.login(school="school-A",subject="learner-A",credential=PASSWORD)
    def test_only_salted_verifier_persisted(self):
        self.login.provision(school="school-A",subject="learner-A",credential=PASSWORD,authorized_operator=True)
        salt,verifier=self.db.execute("SELECT salt,verifier FROM synthetic_login_credentials").fetchone()
        self.assertEqual((len(salt),len(verifier)),(16,32))
        self.assertNotIn(PASSWORD.encode(),salt+verifier)

if __name__=="__main__":
    unittest.main()
