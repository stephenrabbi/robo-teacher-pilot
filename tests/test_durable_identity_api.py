import sqlite3
import unittest
import uuid
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from progress_store.synthetic_api import build_synthetic_progress_app
from progress_store.durable_approvals import create_approval_schema
from progress_store.durable_identity import DurableSyntheticIdentity, create_identity_schema
from progress_store.signed_approval_provider import SignedApprovalVerifier, sign_synthetic_approval
from progress_store.session_auth import issue_test_session

KEY=b"isolated-api-persistence-session-secret-123"
PROVIDER_KEY=b"isolated-api-approval-signing-secret-1234"
def approval(ref, subject):
    return sign_synthetic_approval(dict(issuer="test-school",decision_id=ref,subject=subject,
        school="school-one",reviewer_id="reviewer-one",kind="enrollment",
        approved=True,issued_at=1000,expires_at=1100),secret=PROVIDER_KEY)

class IntegratedDurableIdentityAPITests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(":memory:",check_same_thread=False)
        create_approval_schema(self.db)
        create_identity_schema(self.db)
        verifier=SignedApprovalVerifier(provider_id="test-school",secret=PROVIDER_KEY,clock=lambda:1050)
        self.identity=DurableSyntheticIdentity(self.db,verifier.verify,provider_id="test-school",
            reviewers={"reviewer-one"},signing_key=KEY,clock=lambda:1050)
        self.identity.enroll(approval("approval-A","A"),subject="A",school="school-one")
        self.identity.enroll(approval("approval-B","B"),subject="B",school="school-one")
        self.client=TestClient(build_synthetic_progress_app(enabled=True,connection=self.db,
            signing_key=KEY,enrollment_connection=self.db))
        self.tokens={k:issue_test_session(subject=k,school="school-one",secret=KEY) for k in ("A","B","C")}
    def tearDown(self):
        self.client.close()
        self.db.close()
    def headers(self,subject):
        return {"Authorization":"Bearer "+self.tokens[subject]}
    def event(self):
        return dict(event_id=str(uuid.uuid4()),event_type="practice_completed",
            class_level="JSS2",topic_key="fractions",correct=4,total=5,
            occurred_at=datetime.now(timezone.utc).isoformat())
    def test_enrolled_learners_write_read_separately(self):
        url="/internal/synthetic-progress/events"
        response=self.client.post(url,json=self.event(),headers=self.headers("A"))
        self.assertEqual(response.status_code,201,response.text)
        self.assertEqual(len(self.client.get(url,headers=self.headers("A")).json()["events"]),1)
        self.assertEqual(self.client.get(url,headers=self.headers("B")).json()["events"],[])
    def test_validly_signed_but_unenrolled_session_denied(self):
        url="/internal/synthetic-progress/events"
        self.assertEqual(self.client.get(url,headers=self.headers("C")).status_code,401)
        self.assertEqual(self.client.post(url,json=self.event(),headers=self.headers("C")).status_code,401)
    def test_deleting_enrollment_denies_existing_signed_session(self):
        url="/internal/synthetic-progress/events"
        self.db.execute("DELETE FROM synthetic_enrollments WHERE school=? AND subject=?",("school-one","A"))
        self.db.commit()
        self.assertEqual(self.client.get(url,headers=self.headers("A")).status_code,401)
        self.assertEqual(self.client.post(url,json=self.event(),headers=self.headers("A")).status_code,401)
    def test_expired_session_denied_even_for_enrolled_learner(self):
        from time import time
        old=issue_test_session(subject="A",school="school-one",secret=KEY,now=int(time())-4000)
        url="/internal/synthetic-progress/events"
        headers={"Authorization":"Bearer "+old}
        self.assertEqual(self.client.get(url,headers=headers).status_code,401)
        self.assertEqual(self.client.post(url,json=self.event(),headers=headers).status_code,401)

    def test_recovery_session_preserves_only_correct_learner_progress(self):
        url="/internal/synthetic-progress/events"
        self.assertEqual(self.client.post(url,json=self.event(),headers=self.headers("A")).status_code,201)
        from time import time
        now=int(time())
        verifier=SignedApprovalVerifier(provider_id="test-school",secret=PROVIDER_KEY,clock=lambda:now)
        recovery=DurableSyntheticIdentity(self.db,verifier.verify,provider_id="test-school",
            reviewers={"reviewer-one"},signing_key=KEY,clock=lambda:now)
        proof=sign_synthetic_approval(dict(issuer="test-school",decision_id="recovery-A",
            subject="A",school="school-one",reviewer_id="reviewer-one",kind="recovery",
            approved=True,issued_at=now-1,expires_at=now+120),secret=PROVIDER_KEY)
        challenge=recovery.begin_recovery(proof,subject="A",school="school-one")
        recovered_token=recovery.complete_recovery(subject="A",school="school-one",challenge=challenge)
        headers={"Authorization":"Bearer "+recovered_token}
        self.assertEqual(len(self.client.get(url,headers=headers).json()["events"]),1)
        self.assertEqual(self.client.get(url,headers=self.headers("B")).json()["events"],[])
        with self.assertRaises(PermissionError):
            recovery.complete_recovery(subject="A",school="school-one",challenge=challenge)

    def test_client_scope_override_rejected(self):
        url="/internal/synthetic-progress/events"
        self.assertEqual(self.client.post(url,json=dict(self.event(),subject="B"),
            headers=self.headers("A")).status_code,422)

if __name__=="__main__":
    unittest.main()
