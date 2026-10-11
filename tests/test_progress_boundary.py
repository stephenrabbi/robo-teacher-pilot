import sqlite3
import unittest
import uuid
from progress_store.boundary import ProgressBoundary
from progress_store.prototype import create_schema
from progress_store.session_auth import issue_test_session

KEY = b"isolated-boundary-test-key-not-a-prod-secret-00000"

class ProgressBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        create_schema(self.db)
        self.service = ProgressBoundary(self.db, KEY)
        self.a = issue_test_session(subject="synthetic-A", school="school-one", secret=KEY, now=1000)
        self.b = issue_test_session(subject="synthetic-B", school="school-one", secret=KEY, now=1000)
        self.other_school = issue_test_session(subject="synthetic-A", school="school-two", secret=KEY, now=1000)

    def tearDown(self):
        self.db.close()

    def test_authenticated_submit_and_read(self):
        event = {"event_id":str(uuid.uuid4()),"event_type":"practice_completed","class_level":"JSS2",
                 "topic_key":"fractions","correct":3,"total":5,"occurred_at":"2026-10-11T11:00:00+00:00"}
        self.assertTrue(self.service.submit(bearer_token=self.a,event=event,now=1001))
        self.assertEqual(len(self.service.history(bearer_token=self.a,now=1001)),1)
        self.assertEqual(self.service.history(bearer_token=self.b,now=1001),[])
        self.assertEqual(self.service.history(bearer_token=self.other_school,now=1001),[])

    def test_bad_or_expired_token_fails_closed(self):
        with self.assertRaises(PermissionError):
            self.service.history(bearer_token="forged",now=1001)
        with self.assertRaises(PermissionError):
            self.service.history(bearer_token=self.a,now=2000)

    def test_owner_override_is_rejected(self):
        event = {"event_id":str(uuid.uuid4()),"event_type":"practice_completed","class_level":"JSS2",
                 "topic_key":"fractions","correct":1,"total":2,"occurred_at":"2026-10-11T11:00:00+00:00",
                 "subject":"synthetic-B"}
        with self.assertRaises(ValueError):
            self.service.submit(bearer_token=self.a,event=event,now=1001)

    def test_duplicate_submit_is_idempotent(self):
        event = {"event_id":str(uuid.uuid4()),"event_type":"practice_completed","class_level":"JSS2",
                 "topic_key":"fractions","correct":1,"total":2,"occurred_at":"2026-10-11T11:00:00+00:00"}
        self.assertTrue(self.service.submit(bearer_token=self.a,event=event,now=1001))
        self.assertFalse(self.service.submit(bearer_token=self.a,event=event,now=1001))
        self.assertEqual(len(self.service.history(bearer_token=self.a,now=1001)),1)

if __name__ == "__main__":
    unittest.main()
