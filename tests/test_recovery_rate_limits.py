import os,sqlite3,tempfile,unittest
from progress_store.durable_identity import DurableSyntheticIdentity,create_identity_schema
from progress_store.durable_approvals import create_approval_schema
from progress_store.signed_approval_provider import SignedApprovalVerifier,sign_synthetic_approval

KEY=b"recovery-attempt-test-signing-key-1234567"
PROVIDER=b"recovery-attempt-test-provider-key-12345"

class RecoveryLimitsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=os.path.join(self.tmp.name,"rate.sqlite")
        self.now=1050
        self.open_db()
        self.provider=SignedApprovalVerifier(provider_id="school-provider",secret=PROVIDER,clock=lambda:self.now)
        self.identity=DurableSyntheticIdentity(self.db,self.provider.verify,provider_id="school-provider",
            reviewers={"reviewer"},signing_key=KEY,clock=lambda:self.now)
        self.identity.enroll(self.proof("e1","enrollment"),school="school",subject="learner")
        self.challenge=self.identity.begin_recovery(self.proof("r1","recovery"),school="school",subject="learner")
    def open_db(self):
        self.db=sqlite3.connect(self.path,timeout=5)
        create_approval_schema(self.db)
        create_identity_schema(self.db)
    def proof(self,ref,kind):
        return sign_synthetic_approval(dict(issuer="school-provider",decision_id=ref,
          subject="learner",school="school",reviewer_id="reviewer",kind=kind,
          approved=True,issued_at=1000,expires_at=1100),secret=PROVIDER)
    def reopen(self):
        self.db.close()
        self.open_db()
        self.identity=DurableSyntheticIdentity(self.db,self.provider.verify,provider_id="school-provider",
            reviewers={"reviewer"},signing_key=KEY,clock=lambda:self.now)
    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()
    def test_five_bad_attempts_lock_correct_challenge(self):
        for _ in range(5):
            with self.assertRaises(PermissionError):
                self.identity.complete_recovery(subject="learner",school="school",challenge="wrong")
        with self.assertRaisesRegex(PermissionError,"locked"):
            self.identity.complete_recovery(subject="learner",school="school",challenge=self.challenge)
    def test_lockout_persists_restart_and_resets_after_timeout(self):
        for _ in range(5):
            with self.assertRaises(PermissionError):
                self.identity.complete_recovery(subject="learner",school="school",challenge="bad")
        self.reopen()
        with self.assertRaisesRegex(PermissionError,"locked"):
            self.identity.complete_recovery(subject="learner",school="school",challenge=self.challenge)
        self.now+=901
        # Previous challenge has expired; a newly approved challenge is required.
        self.provider._clock=lambda:self.now
        new=sign_synthetic_approval(dict(issuer="school-provider",decision_id="r2",
          subject="learner",school="school",reviewer_id="reviewer",kind="recovery",
          approved=True,issued_at=self.now-1,expires_at=self.now+100),secret=PROVIDER)
        secret=self.identity.begin_recovery(new,school="school",subject="learner")
        self.assertTrue(self.identity.complete_recovery(subject="learner",school="school",challenge=secret))
    def test_success_clears_prior_failures(self):
        for _ in range(3):
            with self.assertRaises(PermissionError):
                self.identity.complete_recovery(subject="learner",school="school",challenge="bad")
        self.assertTrue(self.identity.complete_recovery(subject="learner",school="school",challenge=self.challenge))
        self.assertIsNone(self.db.execute("SELECT * FROM synthetic_recovery_attempts").fetchone())

if __name__=="__main__":
    unittest.main()
