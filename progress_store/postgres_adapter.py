"""Disposable PostgreSQL progress adapter, never mounted in the live classroom.

A transaction-level enrollment row lock serializes writes with recovery's epoch
update. The session token supplies identity; event payload cannot choose owner.
"""
from datetime import datetime, timezone
from uuid import UUID
from .session_auth import verify_session
from .prototype import ALLOWED_TYPES, ALLOWED_LEVELS

class SyntheticPostgresProgress:
    def __init__(self, connection_factory, signing_key):
        if not callable(connection_factory):
            raise ValueError("Database connection factory required")
        if not isinstance(signing_key, bytes) or len(signing_key) < 32:
            raise ValueError("Server-held signing key required")
        self.connect=connection_factory
        self.key=signing_key

    def _principal(self, conn, token):
        principal=verify_session(token,secret=self.key)
        row=conn.execute("""SELECT session_epoch FROM rt_synthetic.enrollments
            WHERE school=%s AND subject=%s FOR UPDATE""",
            (principal.school,principal.subject)).fetchone()
        if row is None:
            raise PermissionError("Unenrolled learner")
        verify_session(token,secret=self.key,expected_epoch=row[0])
        return principal

    def write(self, *, bearer_token, event):
        if not isinstance(event,dict) or set(event)!={"event_id","event_type","class_level","topic_key","correct","total","occurred_at"}:
            raise ValueError("Invalid event")
        try:
            event_id=UUID(str(event["event_id"]))
            occurred=datetime.fromisoformat(str(event["occurred_at"]).replace("Z","+00:00"))
        except (TypeError,ValueError,AttributeError) as exc:
            raise ValueError("Invalid event ID or timestamp") from exc
        if occurred.tzinfo is None or occurred.utcoffset()!=timezone.utc.utcoffset(occurred):
            raise ValueError("UTC timestamp required")
        correct,total=event["correct"],event["total"]
        topic=event["topic_key"]
        if (event["event_type"] not in ALLOWED_TYPES or event["class_level"] not in ALLOWED_LEVELS
                or not isinstance(topic,str) or not 1<=len(topic)<=80
                or not all(ch.isalnum() or ch in "_-" for ch in topic)
                or type(correct) is not int or type(total) is not int or not 0<=correct<=total<=100):
            raise ValueError("Invalid event values")
        with self.connect() as conn:
            with conn.transaction():
                p=self._principal(conn,bearer_token)
                fields=(p.school,p.subject,event_id,event["event_type"],event["class_level"],topic,
                        correct,total,occurred)
                inserted=conn.execute("""INSERT INTO rt_synthetic.events
                    (school,subject,event_id,event_type,class_level,topic_key,correct_count,total_count,occurred_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT(school,subject,event_id) DO NOTHING RETURNING event_id""",fields).fetchone()
                existing=conn.execute("""SELECT event_type,class_level,topic_key,correct_count,total_count,occurred_at
                    FROM rt_synthetic.events WHERE school=%s AND subject=%s AND event_id=%s""",
                    fields[:3]).fetchone()
                if not existing or existing!=fields[3:]:
                    raise ValueError("Conflicting event ID")
                return inserted is not None

    def history(self, *, bearer_token):
        with self.connect() as conn:
            with conn.transaction():
                p=self._principal(conn,bearer_token)
                return conn.execute("""SELECT event_id,event_type,class_level,topic_key,correct_count,total_count,occurred_at
                    FROM rt_synthetic.events WHERE school=%s AND subject=%s
                    ORDER BY occurred_at,event_id""",(p.school,p.subject)).fetchall()
