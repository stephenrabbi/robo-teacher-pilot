import sqlite3,unittest
from progress_store.prototype import create_schema
from progress_store.durable_identity import create_identity_schema
from progress_store.durable_approvals import create_approval_schema
from progress_store.proof_login import create_login_schema
from progress_store.storage_preflight import check_synthetic_schema

class StoragePreflightTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(":memory:")
    def tearDown(self):
        self.db.close()
    def test_complete_disposable_schema(self):
        create_schema(self.db)
        create_identity_schema(self.db)
        create_approval_schema(self.db)
        create_login_schema(self.db)
        self.assertTrue(check_synthetic_schema(self.db))
    def test_missing_tables_fail_closed(self):
        create_schema(self.db)
        with self.assertRaisesRegex(RuntimeError,"synthetic_enrollments"):
            check_synthetic_schema(self.db)
    def test_missing_session_epoch_detected(self):
        self.db.execute("CREATE TABLE synthetic_enrollments(school TEXT,subject TEXT,reviewer_id TEXT,approved_at INTEGER)")
        with self.assertRaisesRegex(RuntimeError,"session_epoch"):
            check_synthetic_schema(self.db)
    def test_no_implicit_migration(self):
        with self.assertRaises(RuntimeError):
            check_synthetic_schema(self.db)
        self.assertEqual(self.db.execute("SELECT count(*) FROM sqlite_master WHERE type='table'").fetchone()[0],0)

if __name__=="__main__":
    unittest.main()
