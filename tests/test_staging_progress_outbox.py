"""Synthetic-only tests of the isolated staging outbox."""
import tempfile
import unittest
from pathlib import Path
from staging.progress_outbox_prototype import connect, enqueue, pending, mark_synced, mark_failed_attempt

class OutboxPrototypeTests(unittest.TestCase):
    def test_restart_preserves_pending_event(self):
        with tempfile.TemporaryDirectory() as folder:
            file = str(Path(folder) / "outbox.db")
            db = connect(file)
            self.assertEqual(enqueue(db,"practice-qa-1","qa-owner","practice",{"score":75}),"pending")
            db.close()
            db = connect(file)
            self.assertEqual(len(pending(db)),1)
            self.assertTrue(mark_synced(db,"practice-qa-1"))
            self.assertEqual(pending(db),[])
            db.close()

    def test_idempotent_enqueue_and_conflict(self):
        with tempfile.TemporaryDirectory() as folder:
            db=connect(str(Path(folder)/"outbox.db"))
            for _ in range(2):
                self.assertEqual(enqueue(db,"qa-2","qa-owner","diagnostic",{"score":50}),"pending")
            self.assertEqual(len(pending(db)),1)
            with self.assertRaises(ValueError):
                enqueue(db,"qa-2","another-owner","diagnostic",{"score":50})
            db.close()

    def test_retry_limit_marks_failed(self):
        with tempfile.TemporaryDirectory() as folder:
            db=connect(str(Path(folder)/"outbox.db"))
            enqueue(db,"qa-3","qa-owner","practice",{"score":50})
            mark_failed_attempt(db,"qa-3",max_attempts=2)
            self.assertEqual(pending(db)[0]["attempts"],1)
            mark_failed_attempt(db,"qa-3",max_attempts=2)
            self.assertEqual(pending(db),[])
            db.close()

if __name__ == "__main__":
    unittest.main()
