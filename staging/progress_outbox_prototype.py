"""Isolated durable progress outbox prototype.

Not wired to production routes. Use a staging SQLite file for synthetic tests only.
A shared transactional database will be required before multi-instance deployment.
"""
import json
import sqlite3
from datetime import datetime, timezone

def connect(path):
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout=10000")
    connection.execute("""CREATE TABLE IF NOT EXISTS progress_outbox (
      event_id TEXT PRIMARY KEY,
      learner_id TEXT NOT NULL,
      event_type TEXT NOT NULL CHECK(event_type IN ('practice','diagnostic')),
      payload TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','synced','failed')),
      attempts INTEGER NOT NULL DEFAULT 0,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    )""")
    connection.commit()
    return connection

def enqueue(connection, event_id, learner_id, event_type, payload):
    if not event_id or not learner_id or event_type not in ("practice", "diagnostic"):
        raise ValueError("Invalid outbox event")
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a mapping")
    now = datetime.now(timezone.utc).isoformat()
    encoded = json.dumps(payload, separators=(",", ":"), allow_nan=False)
    with connection:
        connection.execute(
            "INSERT OR IGNORE INTO progress_outbox "
            "(event_id, learner_id, event_type, payload, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (event_id, learner_id, event_type, encoded, now, now))
        row = connection.execute("SELECT learner_id,event_type,payload,status FROM progress_outbox WHERE event_id=?", (event_id,)).fetchone()
        if (row["learner_id"], row["event_type"], row["payload"]) != (learner_id, event_type, encoded):
            raise ValueError("Conflicting event ID already exists")
    return row["status"]

def pending(connection, limit=25):
    if not 1 <= limit <= 100:
        raise ValueError("Invalid limit")
    return [dict(row) for row in connection.execute(
        "SELECT event_id,learner_id,event_type,payload,attempts FROM progress_outbox "
        "WHERE status='pending' ORDER BY created_at,event_id LIMIT ?", (limit,))]

def mark_synced(connection, event_id):
    with connection:
        cursor = connection.execute("UPDATE progress_outbox SET status='synced',updated_at=? WHERE event_id=? AND status='pending'",
                                    (datetime.now(timezone.utc).isoformat(), event_id))
    return cursor.rowcount == 1

def mark_failed_attempt(connection, event_id, max_attempts=5):
    with connection:
        connection.execute(
            "UPDATE progress_outbox SET attempts=attempts+1, "
            "status=CASE WHEN attempts+1>=? THEN 'failed' ELSE 'pending' END, updated_at=? "
            "WHERE event_id=? AND status='pending'",
            (max_attempts, datetime.now(timezone.utc).isoformat(), event_id))
