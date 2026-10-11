import sqlite3
import unittest
import uuid
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from progress_store.synthetic_api import build_synthetic_progress_app
from progress_store.session_auth import issue_test_session
from progress_store.durable_identity import create_identity_schema

KEY = b"synthetic-api-test-secret-never-production-0000000"

class SyntheticAPITests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:", check_same_thread=False)
        create_identity_schema(self.db)
        self.db.executemany("INSERT INTO synthetic_enrollments (school,subject,reviewer_id,approved_at) VALUES (?,?,?,?)", [("one","A","test-reviewer",1000),("one","B","test-reviewer",1000)])
        self.db.commit()
        self.client = TestClient(build_synthetic_progress_app(enabled=True, signing_key=KEY, connection=self.db, enrollment_connection=self.db))
        self.a = issue_test_session(subject="A", school="one", secret=KEY)
        self.b = issue_test_session(subject="B", school="one", secret=KEY)

    def tearDown(self):
        self.client.close()
        self.db.close()

    def headers(self, token):
        return {"Authorization": "Bearer " + token}

    def event(self):
        return {"event_id": str(uuid.uuid4()), "event_type": "practice_completed",
                "class_level": "JSS2", "topic_key": "fractions",
                "correct": 3, "total": 5, "occurred_at": datetime.now(timezone.utc).isoformat()}

    def test_disabled_by_default(self):
        with self.assertRaises(RuntimeError):
            build_synthetic_progress_app(signing_key=KEY, connection=self.db)

    def test_enabled_api_without_enrollment_store_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Durable enrollment connection is required"):
            build_synthetic_progress_app(enabled=True, signing_key=KEY, connection=self.db)

    def test_unauthenticated_requests_denied(self):
        self.assertEqual(self.client.get("/internal/synthetic-progress/events").status_code, 401)
        self.assertEqual(self.client.post("/internal/synthetic-progress/events", json=self.event()).status_code, 401)

    def test_write_read_and_separation(self):
        event = self.event()
        url = "/internal/synthetic-progress/events"
        self.assertEqual(self.client.post(url, json=event, headers=self.headers(self.a)).status_code, 201)
        self.assertEqual(len(self.client.get(url, headers=self.headers(self.a)).json()["events"]), 1)
        self.assertEqual(self.client.get(url, headers=self.headers(self.b)).json()["events"], [])
        self.assertEqual(self.client.post(url, json=event, headers=self.headers(self.a)).json(), {"recorded": False})

    def test_rejects_client_owner_override(self):
        payload = dict(self.event(), subject="B", school="one")
        self.assertEqual(self.client.post("/internal/synthetic-progress/events", json=payload, headers=self.headers(self.a)).status_code, 422)

    def test_rejects_forged_session(self):
        self.assertEqual(self.client.get("/internal/synthetic-progress/events", headers=self.headers("forged")).status_code, 401)

if __name__ == "__main__":
    unittest.main()
