"""Isolated prototype for durable learner event storage.

No HTTP routes, production credentials, or real pupil records. Callers must supply
a verified server-side Principal; never construct one from request parameters.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import sqlite3
import uuid

ALLOWED_TYPES = {"practice_completed", "diagnostic_completed", "revision_completed"}
ALLOWED_LEVELS = {"JSS1", "JSS2", "JSS3"}

@dataclass(frozen=True)
class Principal:
    subject: str
    school: str
    verified: bool = False

def _require_principal(principal):
    if not isinstance(principal, Principal) or not principal.verified:
        raise PermissionError("Verified server identity required")
    if not principal.subject or not principal.school:
        raise PermissionError("Missing identity scope")

def create_schema(connection):
    connection.execute("""CREATE TABLE IF NOT EXISTS learner_events (
        school TEXT NOT NULL,
        subject TEXT NOT NULL,
        event_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        class_level TEXT NOT NULL,
        topic_key TEXT NOT NULL,
        correct_count INTEGER NOT NULL,
        total_count INTEGER NOT NULL,
        occurred_at TEXT NOT NULL,
        PRIMARY KEY (school, subject, event_id)
    )""")
    connection.commit()

def record_event(connection, principal, event):
    _require_principal(principal)
    if not isinstance(event, dict):
        raise ValueError("Invalid event")
    allowed = {"event_id", "event_type", "class_level", "topic_key", "correct", "total", "occurred_at"}
    if set(event) != allowed:
        raise ValueError("Unexpected or missing event fields")
    try:
        event_id = str(uuid.UUID(event["event_id"]))
        stamp = datetime.fromisoformat(event["occurred_at"].replace("Z", "+00:00"))
    except (TypeError, ValueError, AttributeError) as error:
        raise ValueError("Invalid ID or timestamp") from error
    if stamp.tzinfo is None or stamp.utcoffset() != timezone.utc.utcoffset(stamp):
        raise ValueError("UTC timestamp required")
    if event["event_type"] not in ALLOWED_TYPES or event["class_level"] not in ALLOWED_LEVELS:
        raise ValueError("Unsupported event type or class")
    topic = event["topic_key"]
    if not isinstance(topic, str) or not (1 <= len(topic) <= 80) or not all(ch.isalnum() or ch in "_-" for ch in topic):
        raise ValueError("Invalid curriculum topic key")
    correct, total = event["correct"], event["total"]
    if type(correct) is not int or type(total) is not int or not 0 <= correct <= total <= 100:
        raise ValueError("Invalid assessment counts")
    fields = (principal.school, principal.subject, event_id, event["event_type"],
              event["class_level"], topic, correct, total, stamp.isoformat())
    # The unique database constraint arbitrates concurrent insert attempts.
    # Once the attempted insertion completes, compare the stored value:
    # identical retries are safe, while conflicting payloads fail closed.
    with connection:
        cursor = connection.execute(
            "INSERT INTO learner_events VALUES (?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT(school, subject, event_id) DO NOTHING", fields)
        inserted = cursor.rowcount == 1
        stored = connection.execute(
            "SELECT event_type,class_level,topic_key,correct_count,total_count,occurred_at "
            "FROM learner_events WHERE school=? AND subject=? AND event_id=?",
            fields[:3]).fetchone()
        if stored is None or tuple(stored) != fields[3:]:
            raise ValueError("Conflicting event ID")
    return inserted

def list_events(connection, principal):
    _require_principal(principal)
    return connection.execute(
        "SELECT event_id,event_type,class_level,topic_key,correct_count,total_count,occurred_at "
        "FROM learner_events WHERE school=? AND subject=? ORDER BY occurred_at,event_id",
        (principal.school, principal.subject)).fetchall()
