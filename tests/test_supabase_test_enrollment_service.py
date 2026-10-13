import hashlib
import unittest
from fastapi import HTTPException
from supabase_test_enrollment_service import EnrollmentService


class FakeStore:
    def __init__(self):
        self.challenges={}
        self.enrolled=set()
    def create(self,uid,digest,ttl_seconds):
        assert ttl_seconds == 300
        self.challenges[digest]=uid
    def consume_and_enroll(self,uid,digest):
        if self.challenges.get(digest) != uid or uid in self.enrolled:
            return None
        del self.challenges[digest]
        self.enrolled.add(uid)
        return "cloud-generated-id"


class TestEnrollmentOrchestration(unittest.TestCase):
    def setUp(self):
        self.store=FakeStore()
        self.service=EnrollmentService(
            verify_token=lambda token: {"token-a":"user-a","token-b":"user-b"}.get(token),
            store=self.store)
    def test_authenticated_issue_and_consume(self):
        challenge=self.service.issue("Bearer token-a")["challenge"]
        self.assertEqual(self.service.consume("Bearer token-a",challenge),
                         {"enrolled":True,"cloud_identity_created":True})
        with self.assertRaises(HTTPException) as cm:
            self.service.consume("Bearer token-a",challenge)
        self.assertEqual(cm.exception.status_code,409)
    def test_wrong_account_cannot_consume(self):
        ticket=self.service.issue("Bearer token-a")["challenge"]
        with self.assertRaises(HTTPException) as cm:
            self.service.consume("Bearer token-b",ticket)
        self.assertEqual(cm.exception.status_code,409)
        self.assertTrue(self.service.consume("Bearer token-a",ticket)["enrolled"])
    def test_missing_or_invalid_auth_fails_closed(self):
        for authorization in ("","Bearer nope","token-a"):
            with self.assertRaises(HTTPException) as cm:
                self.service.issue(authorization)
            self.assertEqual(cm.exception.status_code,401)
    def test_never_accepts_client_selected_identity(self):
        with self.assertRaises(TypeError):
            self.service.issue("Bearer token-a",user_id="user-b")
    def test_proof_is_not_retained_plaintext(self):
        ticket=self.service.issue("Bearer token-a")["challenge"]
        self.assertNotIn(ticket,self.store.challenges)
        self.assertIn(hashlib.sha256(ticket.encode()).digest(),self.store.challenges)


if __name__=="__main__":
    unittest.main()
