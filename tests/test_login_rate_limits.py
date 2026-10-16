import os,sqlite3,tempfile,unittest
from progress_store.durable_identity import create_identity_schema
from progress_store.proof_login import create_login_schema,SyntheticProofLogin
from progress_store.session_auth import verify_session

KEY=b"synthetic-throttle-login-session-secret-12345"
PASSWORD="valid-long-synthetic-credential-2026"

class DurableLoginLimitsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=os.path.join(self.tmp.name,"login.sqlite")
        self.now=1050
        self.open()
        self.db.execute("INSERT INTO synthetic_enrollments (school,subject,reviewer_id,approved_at) VALUES (?,?,?,?)",
                        ("school","learner","reviewer",1000))
        self.db.commit()
        self.login.provision(school="school",subject="learner",credential=PASSWORD,authorized_operator=True)
    def open(self):
        self.db=sqlite3.connect(self.path,timeout=5)
        create_identity_schema(self.db)
        create_login_schema(self.db)
        self.login=SyntheticProofLogin(self.db,signing_key=KEY,clock=lambda:self.now)
    def restart(self):
        self.db.close()
        self.open()
    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()
    def attempt(self,credential):
        return self.login.login(school="school",subject="learner",credential=credential)
    def test_lockout_persists_restart(self):
        for _ in range(5):
            with self.assertRaises(PermissionError):
                self.attempt("bad-password-attempt-2026")
        self.restart()
        with self.assertRaises(PermissionError):
            self.attempt(PASSWORD)
        self.now+=901
        token=self.attempt(PASSWORD)
        self.assertEqual(verify_session(token,secret=KEY,now=self.now).subject,"learner")
    def test_success_resets_failed_counter(self):
        for _ in range(3):
            with self.assertRaises(PermissionError):
                self.attempt("incorrect-login-secret")
        token=self.attempt(PASSWORD)
        self.assertTrue(token)
        self.assertIsNone(self.db.execute("SELECT 1 FROM synthetic_login_attempts").fetchone())
    def test_missing_account_is_not_authenticated(self):
        with self.assertRaises(PermissionError):
            self.login.login(school="school",subject="missing",credential=PASSWORD)

if __name__=="__main__":
    unittest.main()
