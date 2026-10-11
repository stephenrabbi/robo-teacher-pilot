import os,sqlite3,tempfile,threading,time,unittest,uuid
from progress_store.prototype import create_schema
from progress_store.durable_identity import create_identity_schema
from progress_store.boundary import ProgressBoundary
from progress_store.session_auth import issue_test_session

KEY=b"synthetic-atomic-auth-session-key-12345678"

class AtomicAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=os.path.join(self.tmp.name,"atomic.sqlite")
        self.db=sqlite3.connect(self.path,timeout=5)
        create_schema(self.db)
        create_identity_schema(self.db)
        self.db.execute("INSERT INTO synthetic_enrollments(school,subject,reviewer_id,approved_at) VALUES(?,?,?,?)",
                        ("school","student","reviewer",1000))
        self.db.commit()
        self.token=issue_test_session(subject="student",school="school",secret=KEY,session_epoch=0)
        self.event=dict(event_id=str(uuid.uuid4()),event_type="practice_completed",
            class_level="JSS2",topic_key="fractions",correct=3,total=5,
            occurred_at="2026-10-11T12:00:00+00:00")
    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()
    def test_recovery_commits_before_write_authorization(self):
        locked=threading.Event()
        release=threading.Event()
        def revoke():
            conn=sqlite3.connect(self.path,timeout=5)
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("UPDATE synthetic_enrollments SET session_epoch=1 WHERE school='school' AND subject='student'")
            locked.set()
            release.wait(4)
            conn.commit()
            conn.close()
        t=threading.Thread(target=revoke)
        t.start()
        self.assertTrue(locked.wait(3))
        result=[]
        def write():
            conn=sqlite3.connect(self.path,timeout=5)
            try:
                ProgressBoundary(conn,KEY).submit_enrolled(bearer_token=self.token,event=self.event,enrollment_connection=conn)
                result.append("accepted")
            except PermissionError:
                result.append("denied")
            finally:
                conn.close()
        w=threading.Thread(target=write)
        w.start()
        release.set()
        w.join(6)
        t.join(6)
        self.assertFalse(w.is_alive())
        self.assertFalse(t.is_alive())
        self.assertEqual(result,["denied"])
        self.assertEqual(self.db.execute("SELECT count(*) FROM learner_events").fetchone()[0],0)
    def test_separate_authorization_connection_fails_closed(self):
        other=sqlite3.connect(self.path)
        try:
            with self.assertRaises(RuntimeError):
                ProgressBoundary(self.db,KEY).submit_enrolled(
                    bearer_token=self.token,event=self.event,enrollment_connection=other)
        finally:
            other.close()
    def test_valid_enrolled_write(self):
        boundary=ProgressBoundary(self.db,KEY)
        self.assertTrue(boundary.submit_enrolled(bearer_token=self.token,event=self.event,enrollment_connection=self.db))
        self.assertEqual(len(boundary.history_enrolled(bearer_token=self.token,enrollment_connection=self.db)),1)

if __name__=="__main__":
    unittest.main()
