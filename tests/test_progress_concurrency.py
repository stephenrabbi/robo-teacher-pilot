"""Concurrency and replay tests for the isolated synthetic SQLite prototype."""
import os
import sqlite3
import tempfile
import threading
import unittest
import uuid
from progress_store.prototype import Principal, create_schema, record_event, list_events

class ConcurrentProgressTests(unittest.TestCase):
    def setUp(self):
        handle, self.path = tempfile.mkstemp(suffix=".db")
        os.close(handle)
        self.subject = Principal("synthetic-one", "test-school", True)
        connection = sqlite3.connect(self.path)
        create_schema(connection)
        connection.close()

    def tearDown(self):
        os.remove(self.path)

    def event(self):
        return {"event_id":str(uuid.uuid4()),"event_type":"practice_completed",
                "class_level":"JSS2","topic_key":"fractions","correct":3,"total":5,
                "occurred_at":"2026-10-11T12:00:00+00:00"}

    def test_same_event_from_two_connections_is_counted_once(self):
        item = self.event()
        barrier = threading.Barrier(2)
        results = []
        errors = []
        def worker():
            db = sqlite3.connect(self.path, timeout=5)
            try:
                barrier.wait(timeout=5)
                results.append(record_event(db, self.subject, item))
            except Exception as exc:
                errors.append(exc)
            finally:
                db.close()
        threads = [threading.Thread(target=worker) for _ in range(2)]
        for t in threads: t.start()
        for t in threads: t.join(timeout=8)
        self.assertFalse(any(t.is_alive() for t in threads))
        self.assertEqual(errors, [])
        self.assertEqual(sorted(results), [False, True])
        db = sqlite3.connect(self.path)
        self.assertEqual(len(list_events(db, self.subject)), 1)
        db.close()

    def test_conflicting_replay_does_not_overwrite_original(self):
        item = self.event()
        first = sqlite3.connect(self.path)
        self.assertTrue(record_event(first, self.subject, item))
        first.close()
        other = sqlite3.connect(self.path)
        with self.assertRaises(ValueError):
            record_event(other, self.subject, dict(item, correct=4))
        self.assertEqual(list_events(other, self.subject)[0][4:6], (3,5))
        other.close()

    def test_distinct_events_from_separate_connections_both_survive(self):
        one, two = self.event(), self.event()
        first, second = sqlite3.connect(self.path), sqlite3.connect(self.path)
        record_event(first, self.subject, one)
        record_event(second, self.subject, two)
        self.assertEqual(len(list_events(first, self.subject)), 2)
        first.close()
        second.close()

if __name__ == "__main__":
    unittest.main()
