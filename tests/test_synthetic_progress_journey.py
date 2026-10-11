"""Synthetic persistence fixtures; low-level token helper is test-only and not authentication."""
import sqlite3
import tempfile
import unittest
import uuid
from pathlib import Path

from progress_store.enrollment_gateway import ApprovedEnrollment, VerifiedEnrollmentGateway
from progress_store.identity_prototype import TestIdentityAuthority
from progress_store.boundary import ProgressBoundary
from progress_store.session_auth import issue_test_session

KEY = b"synthetic-e2e-secret-not-for-production-123456789"

def practice_event():
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": "practice_completed",
        "class_level": "JSS2",
        "topic_key": "fractions",
        "correct": 4,
        "total": 5,
        "occurred_at": "2026-10-11T11:00:00+00:00",
    }

class SyntheticJourneyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp.name) / "synthetic-progress.sqlite3")
        self.conn = sqlite3.connect(self.db_path)
        from progress_store.prototype import create_schema
        create_schema(self.conn)
        self.boundary = ProgressBoundary(self.conn, KEY)
        self.enrollment = VerifiedEnrollmentGateway(KEY, {"reviewer-one"})
        self.enrollment.approve(
            ApprovedEnrollment("synthetic-A", "school-one", "approval-e2e-001", "reviewer-one"),
            authenticated_reviewer="reviewer-one",
        )

    def tearDown(self):
        self.conn.close()
        self.temp.cleanup()

    def test_approved_learner_recovers_history_in_separate_session_after_restart(self):
        first_device = issue_test_session(subject="synthetic-A", school="school-one", secret=KEY, now=1000)
        item = practice_event()
        self.assertTrue(self.boundary.submit(bearer_token=first_device, event=item, now=1001))
        self.conn.close()
        self.conn = sqlite3.connect(self.db_path)
        self.boundary = ProgressBoundary(self.conn, KEY)
        second_device = issue_test_session(subject="synthetic-A", school="school-one", secret=KEY, now=1100)
        history = self.boundary.history(bearer_token=second_device, now=1101)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0][0], item["event_id"])
        self.assertFalse(self.boundary.submit(bearer_token=second_device, event=item, now=1101))
        self.assertEqual(len(self.boundary.history(bearer_token=second_device, now=1101)), 1)

    def test_other_learner_and_school_cannot_read_history(self):
        self.boundary.submit(
            bearer_token=self.enrollment.issue(subject="synthetic-A", school="school-one", now=1000),
            event=practice_event(), now=1001)
        for subject, school in (("synthetic-B", "school-one"), ("synthetic-A", "school-two")):
            self.enrollment.approve(
                ApprovedEnrollment(subject, school, "approval-separate", "reviewer-one"),
                authenticated_reviewer="reviewer-one")
            token = issue_test_session(subject=subject, school=school, secret=KEY, now=1000)
            self.assertEqual(self.boundary.history(bearer_token=token, now=1001), [])

    def test_recovery_reissues_new_token_but_does_not_change_owner(self):
        # This separate test authority simulates independently approved recovery.
        authority = TestIdentityAuthority(KEY)
        authority.register_approved(subject="synthetic-A", school="school-one", approved=True)
        initial = issue_test_session(subject="synthetic-A", school="school-one", secret=KEY, now=1000)
        self.boundary.submit(bearer_token=initial, event=practice_event(), now=1001)
        challenge = authority.create_recovery_challenge(
            subject="synthetic-A", school="school-one", approved_recovery=True, now=1100)
        recovered = authority.redeem_recovery(
            subject="synthetic-A", school="school-one", challenge=challenge, now=1101)
        self.assertEqual(len(self.boundary.history(bearer_token=recovered, now=1102)), 1)
        with self.assertRaises(PermissionError):
            authority.redeem_recovery(
                subject="synthetic-A", school="school-one", challenge=challenge, now=1102)

    def test_unapproved_second_device_cannot_recover_by_code(self):
        self.assertNotIn(("school-one", "synthetic-B"), self.enrollment._approved)
        self.assertFalse(hasattr(self.enrollment, "issue"))
        with self.assertRaises(PermissionError):
            self.boundary.history(bearer_token="ISE-JSS2-001", now=1001)

if __name__ == "__main__":
    unittest.main()
