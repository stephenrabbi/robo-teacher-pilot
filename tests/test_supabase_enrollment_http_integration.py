"""HTTP integration tests for UNMOUNTED synthetic enrollment service only.

Uses FastAPI TestClient with an isolated fake persistence layer and mock token
verifier. It does not call or modify Supabase or production classroom APIs.
"""
import hashlib
import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from supabase_test_enrollment_service import EnrollmentService, make_test_enrollment_router


class SyntheticStore:
    def __init__(self):
        self.pending = {}
        self.enrolled = set()

    def create(self, uid, digest, ttl_seconds):
        assert ttl_seconds == 300
        self.pending[digest] = uid

    def consume_and_enroll(self, uid, digest):
        if self.pending.get(digest) != uid or uid in self.enrolled:
            return None
        self.pending.pop(digest)
        self.enrolled.add(uid)
        return "CLOUD-TEST"


class TestEnrollmentHTTP(unittest.TestCase):
    def setUp(self):
        self.store = SyntheticStore()
        self.app = FastAPI()
        service = EnrollmentService(
            verify_token=lambda token: {"synthetic-a": "learner-a", "synthetic-b": "learner-b"}.get(token),
            store=self.store,
        )
        self.app.include_router(make_test_enrollment_router(service))
        self.client = TestClient(self.app)
        self.prefix = "/api/internal/supabase-enrollment-test"

    def auth(self, learner):
        return {"Authorization": "Bearer synthetic-" + learner}

    def test_missing_bearer_fails(self):
        response = self.client.post(self.prefix + "/issue")
        self.assertEqual(response.status_code, 401)

    def test_invalid_bearer_fails(self):
        response = self.client.post(self.prefix + "/issue",
                                    headers={"Authorization": "Bearer arbitrary"})
        self.assertEqual(response.status_code, 401)

    def test_full_http_issue_consume_and_replay(self):
        issued = self.client.post(self.prefix + "/issue", headers=self.auth("a"))
        self.assertEqual(issued.status_code, 200)
        proof = issued.json()["challenge"]
        self.assertNotIn(proof, self.store.pending)
        self.assertIn(hashlib.sha256(proof.encode()).digest(), self.store.pending)
        accepted = self.client.post(self.prefix + "/complete", headers=self.auth("a"),
                                    json={"challenge": proof})
        self.assertEqual(accepted.status_code, 200)
        self.assertEqual(accepted.json(), {"enrolled": True, "cloud_identity_created": True})
        replay = self.client.post(self.prefix + "/complete", headers=self.auth("a"),
                                  json={"challenge": proof})
        self.assertEqual(replay.status_code, 409)

    def test_other_account_cannot_consume(self):
        proof = self.client.post(self.prefix + "/issue", headers=self.auth("a")).json()["challenge"]
        stolen = self.client.post(self.prefix + "/complete", headers=self.auth("b"),
                                  json={"challenge": proof})
        self.assertEqual(stolen.status_code, 409)
        owner = self.client.post(self.prefix + "/complete", headers=self.auth("a"),
                                 json={"challenge": proof})
        self.assertEqual(owner.status_code, 200)

    def test_client_cannot_select_account_id(self):
        issued = self.client.post(self.prefix + "/issue", headers=self.auth("a"),
                                  json={"user_id": "learner-b"})
        self.assertEqual(issued.status_code, 200)
        proof = issued.json()["challenge"]
        attempt = self.client.post(self.prefix + "/complete", headers=self.auth("b"),
                                   json={"challenge": proof, "user_id": "learner-a"})
        self.assertEqual(attempt.status_code, 409)


if __name__ == "__main__":
    unittest.main()
