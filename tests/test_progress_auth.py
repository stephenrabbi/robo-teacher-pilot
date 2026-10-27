import sqlite3
import unittest
from progress_store.session_auth import issue_test_session, verify_session
from progress_store.prototype import create_schema, record_event, list_events

SECRET = b"synthetic-only-key-not-for-production-1234567890"
OTHER = b"other-test-only-key-never-use-in-prod-1234567"

class SignedSessionTests(unittest.TestCase):
    def token(self, **kwargs):
        return issue_test_session(subject="learner-one", school="school-one", secret=SECRET, now=1000, **kwargs)

    def test_valid_scoped_session(self):
        principal = verify_session(self.token(), secret=SECRET, now=1001)
        self.assertEqual((principal.subject, principal.school, principal.verified), ("learner-one", "school-one", True))

    def test_expired_and_future_sessions_rejected(self):
        for current_time in (999, 1900):
            with self.assertRaises(PermissionError):
                verify_session(self.token(), secret=SECRET, now=current_time)

    def test_tampering_and_wrong_secret_rejected(self):
        token = self.token()
        with self.assertRaises(PermissionError):
            verify_session(token, secret=OTHER, now=1001)
        body, mac = token.split(".")
        with self.assertRaises(PermissionError):
            verify_session(body + "x." + mac, secret=SECRET, now=1001)

    def test_untrusted_or_malformed_tokens_rejected(self):
        for token in ("", "bad", "a.b.c", "%%%..", None):
            with self.assertRaises(PermissionError):
                verify_session(token, secret=SECRET, now=1001)

    def test_token_scoping_isolation(self):
        import uuid
        db = sqlite3.connect(":memory:")
        create_schema(db)
        a = verify_session(self.token(), secret=SECRET, now=1001)
        btoken = issue_test_session(subject="learner-two", school="school-one", secret=SECRET, now=1000)
        b = verify_session(btoken, secret=SECRET, now=1001)
        item = {"event_id":str(uuid.uuid4()), "event_type":"practice_completed", "class_level":"JSS2",
                "topic_key":"fractions", "correct":3, "total":5, "occurred_at":"2026-10-11T11:00:00+00:00"}
        record_event(db, a, item)
        self.assertEqual(len(list_events(db, a)), 1)
        self.assertEqual(list_events(db, b), [])
        db.close()

    def test_weak_secret_and_long_ttl_rejected(self):
        with self.assertRaises(ValueError):
            issue_test_session(subject="A", school="B", secret=b"short", now=1000)
        with self.assertRaises(ValueError):
            self.token(ttl=3601)

if __name__ == "__main__":
    unittest.main()
