"""Durable, privacy-light state for resumable Autopilot learning sessions.

Only structured session metadata is stored: pseudonymous learner ID, class,
session ID, status, completed-step count, sequence number and timestamps.
Lesson text, answers, transcripts, misconceptions and voice content are never
stored by this module.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import threading
import uuid

import gspread

_HEADER = [
    "Timestamp (UTC)", "Event ID", "Session ID", "Learner ID",
    "Class Level", "Status", "Completed Steps", "Sequence", "Started (UTC)",
]
_OPEN_STATUSES = {"active", "paused"}
_TERMINAL_STATUSES = {"stopped", "complete"}
_RESUME_WINDOW_HOURS = 24

_client = None
_worksheet = None
_memory_events: list[dict] = []
_unsynced_ids: set[str] = set()
_lock = threading.Lock()


def _now() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")


def _sheet_configured() -> bool:
    return bool(os.getenv("GOOGLE_SHEET_ID") and os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))


def _get_worksheet():
    global _client, _worksheet
    if _worksheet is None:
        if _client is None:
            credentials = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
            _client = gspread.service_account_from_dict(credentials)
        spreadsheet = _client.open_by_key(os.environ["GOOGLE_SHEET_ID"])
        try:
            _worksheet = spreadsheet.worksheet("Autopilot Sessions")
            headings = _worksheet.row_values(1)
            for column_index, heading in enumerate(_HEADER, start=1):
                if heading in headings:
                    continue
                current_columns = getattr(_worksheet, "col_count", len(headings))
                if current_columns < column_index:
                    _worksheet.add_cols(column_index - current_columns)
                _worksheet.update_cell(1, column_index, heading)
        except gspread.WorksheetNotFound:
            _worksheet = spreadsheet.add_worksheet(title="Autopilot Sessions", rows=3000, cols=len(_HEADER))
            _worksheet.append_row(_HEADER)
    return _worksheet


def _event_id(session_id: str, sequence: int) -> str:
    return hashlib.sha256(f"{session_id}:{sequence}".encode()).hexdigest()[:32]


def _row_to_event(row: dict) -> dict | None:
    try:
        return {
            "timestamp": str(row.get("Timestamp (UTC)", "")),
            "event_id": str(row.get("Event ID", "")),
            "session_id": str(row.get("Session ID", "")),
            "learner_id": str(row.get("Learner ID", "")),
            "class_level": str(row.get("Class Level", "JSS2") or "JSS2"),
            "status": str(row.get("Status", "active") or "active"),
            "completed_steps": max(0, min(3, int(row.get("Completed Steps", 0) or 0))),
            "sequence": max(0, int(row.get("Sequence", 0) or 0)),
            "started_at": str(row.get("Started (UTC)", "")),
        }
    except (TypeError, ValueError):
        return None


def get_events(learner_id: str | None = None) -> tuple[list[dict], bool]:
    events: list[dict] = []
    synced = False
    if _sheet_configured():
        try:
            for row in _get_worksheet().get_all_records():
                item = _row_to_event(row)
                if item and (learner_id is None or item["learner_id"] == learner_id):
                    events.append(item)
            synced = True
        except Exception as exc:
            print(f"[autopilot_progress] WARNING: failed to load Autopilot sessions: {type(exc).__name__}")
    known = {item["event_id"] for item in events}
    with _lock:
        pending = [
            item.copy() for item in _memory_events
            if item["event_id"] not in known and (learner_id is None or item["learner_id"] == learner_id)
        ]
        pending_unsynced = any(item["event_id"] in _unsynced_ids for item in pending)
    return events + pending, synced and not pending_unsynced


def _latest_by_session(events: list[dict]) -> dict[str, dict]:
    latest: dict[str, dict] = {}
    for item in events:
        session_id = item.get("session_id")
        if not session_id:
            continue
        current = latest.get(session_id)
        if current is None or (item.get("sequence", 0), item.get("timestamp", "")) > (current.get("sequence", 0), current.get("timestamp", "")):
            latest[session_id] = item
    return latest


def _within_resume_window(timestamp: str) -> bool:
    try:
        parsed = datetime.datetime.fromisoformat(timestamp)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=datetime.UTC)
        age = datetime.datetime.now(datetime.UTC) - parsed.astimezone(datetime.UTC)
        return datetime.timedelta(0) <= age <= datetime.timedelta(hours=_RESUME_WINDOW_HOURS)
    except (TypeError, ValueError):
        return False


def _current_open_session(learner_id: str, class_level: str) -> tuple[dict | None, bool]:
    events, synced = get_events(learner_id)
    latest = [
        item for item in _latest_by_session(events).values()
        if item.get("class_level") == class_level
        and item.get("status") in _OPEN_STATUSES
        and item.get("completed_steps", 0) < 3
        and _within_resume_window(item.get("timestamp", ""))
    ]
    if not latest:
        return None, synced
    latest.sort(key=lambda item: (item.get("timestamp", ""), item.get("sequence", 0)), reverse=True)
    return latest[0], synced


def _latest_owned_session(learner_id: str, class_level: str, session_id: str) -> tuple[dict | None, bool]:
    events, synced = get_events(learner_id)
    matches = [
        item for item in events
        if item.get("session_id") == session_id and item.get("class_level") == class_level
    ]
    if not matches:
        return None, synced
    matches.sort(key=lambda item: (item.get("sequence", 0), item.get("timestamp", "")), reverse=True)
    return matches[0], synced


def _stage_event(
    *, learner_id: str, class_level: str, session_id: str, status: str,
    completed_steps: int, sequence: int, started_at: str,
) -> dict:
    event = {
        "timestamp": _now(),
        "event_id": _event_id(session_id, sequence),
        "session_id": session_id,
        "learner_id": learner_id,
        "class_level": class_level,
        "status": status,
        "completed_steps": max(0, min(3, int(completed_steps))),
        "sequence": sequence,
        "started_at": started_at,
    }
    with _lock:
        existing = next((item for item in _memory_events if item["event_id"] == event["event_id"]), None)
        if existing:
            return existing.copy()
        _memory_events.append(event)
        _unsynced_ids.add(event["event_id"])
    return event.copy()


def persist_session_event(event_id: str) -> bool:
    with _lock:
        event = next((item.copy() for item in _memory_events if item["event_id"] == event_id), None)
        needs_sync = event_id in _unsynced_ids
    if not event or not needs_sync:
        return True
    if not _sheet_configured():
        return False
    try:
        _get_worksheet().append_row([
            event["timestamp"], event["event_id"], event["session_id"], event["learner_id"],
            event["class_level"], event["status"], event["completed_steps"], event["sequence"], event["started_at"],
        ])
        with _lock:
            _unsynced_ids.discard(event_id)
        return True
    except Exception as exc:
        print(f"[autopilot_progress] WARNING: failed to save Autopilot session: {type(exc).__name__}")
        return False


def _public(event: dict | None, synced: bool, *, resumed: bool = False) -> dict:
    if not event:
        return {"resumable": False, "session": None, "storage_synced": synced}
    return {
        "resumable": event.get("status") in _OPEN_STATUSES and event.get("completed_steps", 0) < 3,
        "resumed": resumed,
        "session": {
            "session_id": event["session_id"],
            "class_level": event["class_level"],
            "status": event["status"],
            "completed_steps": event["completed_steps"],
            "started_at": event["started_at"],
            "updated_at": event["timestamp"],
        },
        "storage_synced": synced and event["event_id"] not in _unsynced_ids,
        "event_id": event["event_id"],
    }


def session_status(learner_id: str, class_level: str) -> dict:
    event, synced = _current_open_session(learner_id, class_level)
    return _public(event, synced)


def start_or_resume_session(learner_id: str, class_level: str) -> dict:
    current, synced = _current_open_session(learner_id, class_level)
    if current:
        if current["status"] == "paused":
            current = _stage_event(
                learner_id=learner_id,
                class_level=class_level,
                session_id=current["session_id"],
                status="active",
                completed_steps=current["completed_steps"],
                sequence=current["sequence"] + 1,
                started_at=current["started_at"],
            )
        return _public(current, synced, resumed=True)

    started_at = _now()
    session_id = uuid.uuid4().hex[:24]
    event = _stage_event(
        learner_id=learner_id,
        class_level=class_level,
        session_id=session_id,
        status="active",
        completed_steps=0,
        sequence=0,
        started_at=started_at,
    )
    return _public(event, synced, resumed=False)


def transition_session(
    learner_id: str,
    class_level: str,
    session_id: str,
    status: str,
    completed_steps: int,
) -> dict:
    if status not in _OPEN_STATUSES | _TERMINAL_STATUSES:
        raise ValueError("invalid_status")
    current, synced = _latest_owned_session(learner_id, class_level, session_id)
    if current is None:
        raise ValueError("session_not_found")
    if current["status"] in _TERMINAL_STATUSES:
        return _public(current, synced)

    completed = max(current["completed_steps"], min(3, int(completed_steps)))
    if status == "complete":
        completed = 3
    if current["status"] == status and current["completed_steps"] == completed:
        return _public(current, synced)

    event = _stage_event(
        learner_id=learner_id,
        class_level=class_level,
        session_id=session_id,
        status=status,
        completed_steps=completed,
        sequence=current["sequence"] + 1,
        started_at=current["started_at"],
    )
    return _public(event, synced)


def reset_for_tests() -> None:
    """Clear process-local state; test helper only."""
    global _worksheet, _client
    with _lock:
        _memory_events.clear()
        _unsynced_ids.clear()
    _worksheet = None
    _client = None
