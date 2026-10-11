import os, sqlite3, tempfile, unittest
from progress_store.durable_approvals import create_approval_schema
from progress_store.durable_identity import create_identity_schema, DurableSyntheticIdentity
from progress_store.signed_approval_provider import SignedApprovalVerifier, sign_synthetic_approval
from progress_store.session_auth import verify_session

PROVIDER_KEY=b"synthetic-provider-key-for-tests-123456789"
SIGNING_KEY=b"synthetic-session-signing-key-1234567890"
def evidence(ref,kind="enrollment",subject="student-a",school="school-a"):
    return sign_synthetic_approval(dict(issuer="trusted-school",decision_id=ref,
        subject=subject,school=school,reviewer_id="reviewer-a",kind=kind,approved=True,
        issued_at=1000,expires_at=1100),secret=PROVIDER_KEY)

class DurableIdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=os.path.join(self.tmp.name,"identity.sqlite")
        self.db=sqlite3.connect(self.path,timeout=5)
        self.db.execute("PRAGMA foreign_keys=ON")
        create_approval_schema(self.db)
        create_identity_schema(self.db)
        self.verifier=SignedApprovalVerifier(provider_id="trusted-school",secret=PROVIDER_KEY,clock=lambda:1050)
        self.new_client()
    def new_client(self):
        self.identity=DurableSyntheticIdentity(self.db,self.verifier.verify,provider_id="trusted-school",
            reviewers={"reviewer-a"},signing_key=SIGNING_KEY,clock=lambda:1050)
    def restart(self):
        self.db.close()
        self.db=sqlite3.connect(self.path,timeout=5)
        self.db.execute("PRAGMA foreign_keys=ON")
        self.new_client()
    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()
    def test_enrollment_survives_restart(self):
        self.identity.enroll(evidence("e1"),subject="student-a",school="school-a")
        self.restart()
        token=self.identity.issue(subject="student-a",school="school-a")
        p=verify_session(token,secret=SIGNING_KEY,now=1050)
        self.assertEqual((p.subject,p.school),("student-a","school-a"))
        with self.assertRaises(PermissionError):
            self.identity.issue(subject="student-b",school="school-a")
    def test_recovery_survives_restart_and_is_single_use(self):
        self.identity.enroll(evidence("e1"),subject="student-a",school="school-a")
        challenge=self.identity.begin_recovery(evidence("r1","recovery"),subject="student-a",school="school-a")
        self.restart()
        token=self.identity.complete_recovery(subject="student-a",school="school-a",challenge=challenge)
        self.assertEqual(verify_session(token,secret=SIGNING_KEY,now=1050).subject,"student-a")
        with self.assertRaises(PermissionError):
            self.identity.complete_recovery(subject="student-a",school="school-a",challenge=challenge)
    def test_failed_recovery_cannot_consume_challenge(self):
        self.identity.enroll(evidence("e1"),subject="student-a",school="school-a")
        challenge=self.identity.begin_recovery(evidence("r1","recovery"),subject="student-a",school="school-a")
        with self.assertRaises(PermissionError):
            self.identity.complete_recovery(subject="student-a",school="school-a",challenge="incorrect")
        self.assertTrue(self.identity.complete_recovery(subject="student-a",school="school-a",challenge=challenge))
    def test_reuse_and_wrong_scope_rejected(self):
        e=evidence("e1")
        with self.assertRaises(PermissionError):
            self.identity.enroll(e,subject="student-b",school="school-a")
        self.identity.enroll(e,subject="student-a",school="school-a")
        self.restart()
        with self.assertRaises(PermissionError):
            self.identity.enroll(e,subject="student-a",school="school-a")
        with self.assertRaises(PermissionError):
            self.identity.begin_recovery(evidence("r1","recovery",subject="student-b"),subject="student-b",school="school-a")
    def test_second_recovery_invalidates_first(self):
        self.identity.enroll(evidence("e1"),subject="student-a",school="school-a")
        first=self.identity.begin_recovery(evidence("r1","recovery"),subject="student-a",school="school-a")
        second=self.identity.begin_recovery(evidence("r2","recovery"),subject="student-a",school="school-a")
        with self.assertRaises(PermissionError):
            self.identity.complete_recovery(subject="student-a",school="school-a",challenge=first)
        self.assertTrue(self.identity.complete_recovery(subject="student-a",school="school-a",challenge=second))

if __name__=="__main__":
    unittest.main()
