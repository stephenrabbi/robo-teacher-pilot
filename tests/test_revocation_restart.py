"""Synthetic-only tests of durable epoch revocation with separate DB connections."""
import os,sqlite3,tempfile,threading,unittest
from progress_store.durable_identity import create_identity_schema,DurableSyntheticIdentity
from progress_store.durable_approvals import create_approval_schema
from progress_store.session_auth import issue_test_session,verify_session
from progress_store.signed_approval_provider import SignedApprovalVerifier,sign_synthetic_approval

KEY=b"durable-revocation-test-key-123456789"
PKEY=b"durable-revocation-provider-key-1234567"

class RevocationRestartTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=os.path.join(self.tmp.name,"identity.sqlite")
        self.db=sqlite3.connect(self.path,timeout=10)
        create_approval_schema(self.db)
        create_identity_schema(self.db)
        self.db.execute("INSERT INTO synthetic_enrollments (school,subject,reviewer_id,approved_at) VALUES (?,?,?,?)",
                        ("school","learner","reviewer",1000))
        self.db.commit()
    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()
    def identity(self,db):
        verifier=SignedApprovalVerifier(provider_id="school-provider",secret=PKEY,clock=lambda:1050)
        return DurableSyntheticIdentity(db,verifier.verify,provider_id="school-provider",
            reviewers={"reviewer"},signing_key=KEY,clock=lambda:1050)
    def proof(self):
        return sign_synthetic_approval(dict(issuer="school-provider",decision_id="r1",
           subject="learner",school="school",reviewer_id="reviewer",kind="recovery",
           approved=True,issued_at=1000,expires_at=1100),secret=PKEY)
    def test_old_token_stays_revoked_after_restart(self):
        old=issue_test_session(subject="learner",school="school",secret=KEY,now=1050,session_epoch=0)
        challenge=self.identity(self.db).begin_recovery(self.proof(),subject="learner",school="school")
        fresh=self.identity(self.db).complete_recovery(subject="learner",school="school",challenge=challenge)
        self.db.close()
        self.db=sqlite3.connect(self.path,timeout=10)
        epoch=self.db.execute("SELECT session_epoch FROM synthetic_enrollments").fetchone()[0]
        with self.assertRaises(PermissionError):
            verify_session(old,secret=KEY,now=1050,expected_epoch=epoch)
        self.assertEqual(verify_session(fresh,secret=KEY,now=1050,expected_epoch=epoch).subject,"learner")
    def test_concurrent_recovery_only_one_challenge_redemption(self):
        challenge=self.identity(self.db).begin_recovery(self.proof(),subject="learner",school="school")
        outputs=[]
        lock=threading.Lock()
        def redeem():
            conn=sqlite3.connect(self.path,timeout=10)
            try:
                token=self.identity(conn).complete_recovery(subject="learner",school="school",challenge=challenge)
                result=("ok",token)
            except PermissionError:
                result=("denied",None)
            finally:
                conn.close()
            with lock:
                outputs.append(result)
        threads=[threading.Thread(target=redeem) for _ in range(2)]
        for t in threads:t.start()
        for t in threads:t.join()
        self.assertEqual(sorted(x[0] for x in outputs),["denied","ok"])
        self.assertEqual(self.db.execute("SELECT session_epoch FROM synthetic_enrollments").fetchone()[0],1)

if __name__=="__main__":
    unittest.main()
