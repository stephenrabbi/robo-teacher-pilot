"""Integration tests against a real disposable PostgreSQL CI service only."""
import os
import threading
import unittest
from pathlib import Path
import psycopg
from integration_research.postgres_atomic_activation import SyntheticPostgresActivation

DSN=os.environ.get("SYNTHETIC_PG_TEST_DSN")
@unittest.skipUnless(DSN,"Dedicated disposable PostgreSQL service required")
class PostgresAtomicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DSN:return
        with psycopg.connect(DSN) as db:
            db.execute("DROP SCHEMA IF EXISTS synthetic_identity_lab CASCADE")
            db.execute(Path("integration_research/sql/001_atomic_synthetic_postgres.sql").read_text())
    def setUp(self):
        with psycopg.connect(DSN) as db:
            db.execute("TRUNCATE synthetic_identity_lab.learner_activations, synthetic_identity_lab.approval_redemptions")
        self.adapter=SyntheticPostgresActivation(lambda:psycopg.connect(DSN),
            lambda proof,school,learner: proof=="synthetic-verified-proof" and school=="school-A" and learner=="learner-A")
    def test_committed_once_and_replay_denied(self):
        self.assertTrue(self.adapter.activate(school="school-A",learner="learner-A",approval_proof="synthetic-verified-proof"))
        with self.assertRaises(psycopg.errors.UniqueViolation):
            self.adapter.activate(school="school-A",learner="learner-A",approval_proof="synthetic-verified-proof")
        with psycopg.connect(DSN) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM synthetic_identity_lab.learner_activations").fetchone()[0],1)
            self.assertEqual(db.execute("SELECT count(*) FROM synthetic_identity_lab.approval_redemptions").fetchone()[0],1)
    def test_failed_second_insert_rolls_back_redemption(self):
        with psycopg.connect(DSN) as db:
            db.execute("""CREATE OR REPLACE FUNCTION synthetic_identity_lab.block_insert() RETURNS trigger AS $$
              BEGIN RAISE EXCEPTION 'synthetic account failure'; END; $$ LANGUAGE plpgsql""")
            db.execute("""CREATE TRIGGER block_insert BEFORE INSERT ON synthetic_identity_lab.learner_activations
                FOR EACH ROW EXECUTE FUNCTION synthetic_identity_lab.block_insert()""")
        try:
            with self.assertRaises(psycopg.errors.RaiseException):
                self.adapter.activate(school="school-A",learner="learner-A",approval_proof="synthetic-verified-proof")
            with psycopg.connect(DSN) as db:
                self.assertEqual(db.execute("SELECT count(*) FROM synthetic_identity_lab.approval_redemptions").fetchone()[0],0)
        finally:
            with psycopg.connect(DSN) as db:
                db.execute("DROP TRIGGER IF EXISTS block_insert ON synthetic_identity_lab.learner_activations")
    def test_concurrent_replay_one_success(self):
        barrier=threading.Barrier(2)
        results=[]
        def worker():
            barrier.wait()
            try:
                self.adapter.activate(school="school-A",learner="learner-A",approval_proof="synthetic-verified-proof")
                results.append("ok")
            except psycopg.errors.UniqueViolation:
                results.append("replay")
        threads=[threading.Thread(target=worker) for _ in range(2)]
        for t in threads:t.start()
        for t in threads:t.join(timeout=15)
        self.assertFalse(any(t.is_alive() for t in threads))
        self.assertCountEqual(results,["ok","replay"])
    def test_rejects_unverified_proof_without_db_changes(self):
        with self.assertRaises(PermissionError):
            self.adapter.activate(school="school-A",learner="learner-A",approval_proof="forged")
        with psycopg.connect(DSN) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM synthetic_identity_lab.approval_redemptions").fetchone()[0],0)

if __name__=="__main__":
    unittest.main()
