import sqlite3
import unittest
import uuid
from datetime import datetime, timezone
from progress_store.prototype import Principal, create_schema, record_event, list_events

def event():
    return {"event_id": str(uuid.uuid4()), "event_type": "practice_completed",
            "class_level": "JSS2", "topic_key": "fractions",
            "correct": 3, "total": 5,
            "occurred_at": datetime.now(timezone.utc).isoformat()}

class StorageSafetyTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        create_schema(self.db)
        self.a = Principal("synthetic-A", "school-one", True)
        self.b = Principal("synthetic-B", "school-one", True)
        self.other = Principal("synthetic-A", "school-two", True)

    def tearDown(self):
        self.db.close()

    def test_unverified_principal_denied(self):
        with self.assertRaises(PermissionError):
            list_events(self.db, Principal("synthetic-A", "school-one"))
        with self.assertRaises(PermissionError):
            record_event(self.db, None, event())

    def test_isolation_between_learners_and_schools(self):
        record_event(self.db, self.a, event())
        self.assertEqual(len(list_events(self.db, self.a)), 1)
        self.assertEqual(list_events(self.db, self.b), [])
        self.assertEqual(list_events(self.db, self.other), [])

    def test_duplicate_retry_does_not_double_count(self):
        item = event()
        self.assertTrue(record_event(self.db, self.a, item))
        self.assertFalse(record_event(self.db, self.a, item))
        self.assertEqual(len(list_events(self.db, self.a)), 1)
        changed = dict(item, correct=4)
        with self.assertRaises(ValueError):
            record_event(self.db, self.a, changed)

    def test_reject_identity_override_and_bad_counts(self):
        item = dict(event(), subject="synthetic-B")
        with self.assertRaises(ValueError):
            record_event(self.db, self.a, item)
        item = dict(event(), total=-1)
        with self.assertRaises(ValueError):
            record_event(self.db, self.a, item)

    def test_database_restart_retains_events(self):
        # A disk-backed test uses a temporary file rather than real data.
        import tempfile, os
        fd, filename = tempfile.mkstemp()
        os.close(fd)
        try:
            disk = sqlite3.connect(filename)
            create_schema(disk)
            record_event(disk, self.a, event())
            disk.close()
            again = sqlite3.connect(filename)
            self.assertEqual(len(list_events(again, self.a)), 1)
            again.close()
        finally:
            os.remove(filename)

if __name__ == "__main__":
    unittest.main()
