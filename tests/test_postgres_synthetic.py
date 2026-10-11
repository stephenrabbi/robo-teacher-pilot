"""Disposable PostgreSQL integration tests: never connect to learner/production databases."""
import os, pathlib, threading, uuid, unittest
import psycopg
from psycopg.errors import UniqueViolation, ForeignKeyViolation
from progress_store.postgres_adapter import SyntheticPostgresProgress
from progress_store.session_auth import issue_test_session

DSN=os.environ.get("ROBO_SYNTHETIC_PG_DSN")
SQL=pathlib.Path(__file__).resolve().parents[1]/"progress_store/postgres/0001_synthetic_schema.sql"

@unittest.skipUnless(DSN and "localhost" in DSN, "Explicit local disposable Postgres required")
class SyntheticPostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db=psycopg.connect(DSN)
        cls.db.execute("DROP SCHEMA IF EXISTS rt_synthetic CASCADE")
        cls.db.commit()
        cls.db.execute(SQL.read_text())
        cls.db.commit()
    @classmethod
    def tearDownClass(cls):
        cls.db.execute("DROP SCHEMA IF EXISTS rt_synthetic CASCADE")
        cls.db.commit()
        cls.db.close()
    def setUp(self):
        self.db.execute("TRUNCATE rt_synthetic.events, rt_synthetic.enrollments CASCADE")
        self.db.execute("INSERT INTO rt_synthetic.enrollments(school,subject,reviewer_id,approved_at) VALUES ('school','A','reviewer',1000),('school','B','reviewer',1000)")
        self.db.commit()
    def test_adapter_scoping_replay_and_revocation(self):
        adapter=SyntheticPostgresProgress(lambda:psycopg.connect(DSN),b"postgres-disposable-signing-secret-12345")
        key=b"postgres-disposable-signing-secret-12345"
        token_a=issue_test_session(subject="A",school="school",secret=key,session_epoch=0)
        token_b=issue_test_session(subject="B",school="school",secret=key,session_epoch=0)
        item=dict(event_id=str(uuid.uuid4()),event_type="practice_completed",
                  class_level="JSS2",topic_key="fractions",correct=3,total=5,
                  occurred_at="2026-10-11T12:00:00+00:00")
        self.assertTrue(adapter.write(bearer_token=token_a,event=item))
        self.assertFalse(adapter.write(bearer_token=token_a,event=item))
        self.assertEqual(len(adapter.history(bearer_token=token_a)),1)
        self.assertEqual(adapter.history(bearer_token=token_b),[])
        with self.assertRaises(ValueError):
            adapter.write(bearer_token=token_a,event=dict(item,correct=4))
        self.db.execute("UPDATE rt_synthetic.enrollments SET session_epoch=1 WHERE school='school' AND subject='A'")
        self.db.commit()
        with self.assertRaises(PermissionError):
            adapter.write(bearer_token=token_a,event=dict(item,event_id=str(uuid.uuid4())))
        with self.assertRaises(PermissionError):
            adapter.history(bearer_token=token_a)
        refreshed=issue_test_session(subject="A",school="school",secret=key,session_epoch=1)
        self.assertEqual(len(adapter.history(bearer_token=refreshed)),1)

    def test_scoped_event_and_foreign_key(self):
        event_id=uuid.uuid4()
        self.db.execute("""INSERT INTO rt_synthetic.events
            (school,subject,event_id,event_type,class_level,topic_key,correct_count,total_count,occurred_at)
            VALUES ('school','A',%s,'practice_completed','JSS2','fractions',3,5,now())""",(event_id,))
        self.db.commit()
        self.assertEqual(self.db.execute("SELECT count(*) FROM rt_synthetic.events WHERE subject='B'").fetchone()[0],0)
        with self.assertRaises(ForeignKeyViolation):
            self.db.execute("""INSERT INTO rt_synthetic.events
              VALUES ('school','missing',%s,'practice_completed','JSS2','fractions',3,5,now())""",(uuid.uuid4(),))
        self.db.rollback()
    def test_replay_uniqueness(self):
        item=uuid.uuid4()
        for i in range(2):
            try:
                self.db.execute("""INSERT INTO rt_synthetic.events
                    VALUES ('school','A',%s,'practice_completed','JSS2','fractions',3,5,now())""",(item,))
                self.db.commit()
            except UniqueViolation:
                self.db.rollback()
                self.assertEqual(i,1)
        self.assertEqual(self.db.execute("SELECT count(*) FROM rt_synthetic.events").fetchone()[0],1)
    def test_revocation_locks_and_blocks_stale_write(self):
        revoked=threading.Event();release=threading.Event();out=[]
        def recovery():
            with psycopg.connect(DSN) as conn:
                conn.execute("UPDATE rt_synthetic.enrollments SET session_epoch=session_epoch+1 WHERE school='school' AND subject='A'")
                revoked.set()
                release.wait(5)
        def writer():
            with psycopg.connect(DSN) as conn:
                row=conn.execute("SELECT session_epoch FROM rt_synthetic.enrollments WHERE school='school' AND subject='A' FOR UPDATE").fetchone()
                if row[0]!=0:
                    out.append("denied")
                    return
                conn.execute("""INSERT INTO rt_synthetic.events VALUES
                  ('school','A',%s,'practice_completed','JSS2','fractions',3,5,now())""",(uuid.uuid4(),))
                out.append("accepted")
        a=threading.Thread(target=recovery)
        b=threading.Thread(target=writer)
        a.start()
        self.assertTrue(revoked.wait(5))
        b.start()
        release.set()
        a.join(8);b.join(8)
        self.assertFalse(a.is_alive() or b.is_alive())
        self.assertEqual(out,["denied"])
        self.assertEqual(self.db.execute("SELECT count(*) FROM rt_synthetic.events").fetchone()[0],0)

if __name__=="__main__":
    unittest.main()
