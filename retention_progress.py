"""Privacy-light spaced-review scheduling derived from confirmed mastery.

Retention Memory stores only structured scheduling metadata. It never stores
lesson text, assessment questions, answer choices, transcripts or voice data.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import threading

import gspread

_HEADER = [
    "Timestamp (UTC)", "Event ID", "Learner ID", "Learner Code",
    "Class Level", "Topic", "Outcome", "Interval Days", "Next Review (UTC)",
    "Source Event ID",
]
_INTERVALS = (1, 2, 7, 21, 45)
_INITIAL_INTERVAL_DAYS = 2
_LAPSE_INTERVAL_DAYS = 1

_client = None
_worksheet = None
_memory_records: list[dict] = []
_unsynced_ids: set[str] = set()
_lock = threading.Lock()


def _now_dt() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


def _iso(value: datetime.datetime) -> str:
    return value.astimezone(datetime.UTC).isoformat(timespec="seconds")


def _parse(value: str) -> datetime.datetime | None:
    try:
        parsed = datetime.datetime.fromisoformat(str(value or ""))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=datetime.UTC)
        return parsed.astimezone(datetime.UTC)
    except (TypeError, ValueError):
        return None


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
            _worksheet = spreadsheet.worksheet("Retention Memory")
            headings = _worksheet.row_values(1)
            for column_index, heading in enumerate(_HEADER, start=1):
                if heading in headings:
                    continue
                current_columns = getattr(_worksheet, "col_count", len(headings))
                if current_columns < column_index:
                    _worksheet.add_cols(column_index - current_columns)
                _worksheet.update_cell(1, column_index, heading)
        except gspread.WorksheetNotFound:
            _worksheet = spreadsheet.add_worksheet(title="Retention Memory", rows=3000, cols=len(_HEADER))
            _worksheet.append_row(_HEADER)
    return _worksheet


def _event_id(source_event_id: str, outcome: str) -> str:
    return hashlib.sha256(f"retention:{source_event_id}:{outcome}".encode()).hexdigest()[:32]


def _row_to_record(row: dict) -> dict | None:
    try:
        return {
            "timestamp": str(row.get("Timestamp (UTC)", "")),
            "event_id": str(row.get("Event ID", "")),
            "learner_id": str(row.get("Learner ID", "")),
            "learner_code": str(row.get("Learner Code", "")).strip().upper(),
            "class_level": str(row.get("Class Level", "JSS2") or "JSS2"),
            "topic": str(row.get("Topic", "")),
            "outcome": str(row.get("Outcome", "scheduled") or "scheduled"),
            "interval_days": max(1, int(row.get("Interval Days", _INITIAL_INTERVAL_DAYS) or _INITIAL_INTERVAL_DAYS)),
            "next_review_at": str(row.get("Next Review (UTC)", "")),
            "source_event_id": str(row.get("Source Event ID", "")),
            "synthetic": False,
        }
    except (TypeError, ValueError):
        return None


def get_records(learner_id: str | None = None) -> tuple[list[dict], bool]:
    records: list[dict] = []
    synced = False
    if _sheet_configured():
        try:
            for row in _get_worksheet().get_all_records():
                item = _row_to_record(row)
                if item and (learner_id is None or item["learner_id"] == learner_id):
                    records.append(item)
            synced = True
        except Exception as exc:
            print(f"[retention_progress] WARNING: failed to load retention memory: {type(exc).__name__}")
    known = {item["event_id"] for item in records}
    with _lock:
        pending = [
            item.copy() for item in _memory_records
            if item["event_id"] not in known and (learner_id is None or item["learner_id"] == learner_id)
        ]
        pending_unsynced = any(item["event_id"] in _unsynced_ids for item in pending)
    return records + pending, synced and not pending_unsynced


def _latest_retention(learner_id: str, class_level: str, topic: str) -> tuple[dict | None, bool]:
    records, synced = get_records(learner_id)
    matches = [
        item for item in records
        if item.get("class_level") == class_level and item.get("topic") == topic
    ]
    if not matches:
        return None, synced
    matches.sort(key=lambda item: item.get("timestamp", ""))
    return matches[-1], synced


def _synthetic_from_mastery(learner_id: str, class_level: str, topic: str) -> dict | None:
    # Lazy import avoids coupling mastery module initialization to retention IO.
    from mastery_progress import get_records as get_mastery_records

    records, _ = get_mastery_records(learner_id)
    matches = [
        item for item in records
        if item.get("class_level") == class_level and item.get("topic") == topic
    ]
    if not matches:
        return None
    matches.sort(key=lambda item: item.get("timestamp", ""))
    latest = matches[-1]
    if latest.get("state") != "mastered":
        return None
    mastered_at = _parse(latest.get("timestamp", ""))
    if not mastered_at:
        return None
    return {
        "timestamp": latest.get("timestamp", ""),
        "event_id": "",
        "learner_id": learner_id,
        "learner_code": latest.get("learner_code", ""),
        "class_level": class_level,
        "topic": topic,
        "outcome": "scheduled",
        "interval_days": _INITIAL_INTERVAL_DAYS,
        "next_review_at": _iso(mastered_at + datetime.timedelta(days=_INITIAL_INTERVAL_DAYS)),
        "source_event_id": latest.get("event_id", ""),
        "synthetic": True,
    }


def topic_status(learner_id: str, class_level: str, topic: str) -> tuple[dict | None, bool]:
    latest, synced = _latest_retention(learner_id, class_level, topic)
    if latest:
        return latest, synced
    return _synthetic_from_mastery(learner_id, class_level, topic), synced


def is_review_due(learner_id: str, class_level: str, topic: str, *, now: datetime.datetime | None = None) -> bool:
    status, _ = topic_status(learner_id, class_level, topic)
    if not status or status.get("outcome") == "lapse":
        return False
    next_review = _parse(status.get("next_review_at", ""))
    return bool(next_review and next_review <= (now or _now_dt()))


def _next_success_interval(current: int) -> int:
    current = max(1, int(current or _INITIAL_INTERVAL_DAYS))
    for interval in _INTERVALS:
        if interval > current:
            return interval
    return _INTERVALS[-1]


def _stage(
    *, source_event_id: str, learner_id: str, learner_code: str, class_level: str,
    topic: str, outcome: str, interval_days: int,
) -> dict:
    event_id = _event_id(source_event_id, outcome)
    now = _now_dt()
    record = {
        "timestamp": _iso(now),
        "event_id": event_id,
        "learner_id": learner_id,
        "learner_code": learner_code.strip().upper(),
        "class_level": class_level,
        "topic": topic,
        "outcome": outcome,
        "interval_days": max(1, int(interval_days)),
        "next_review_at": _iso(now + datetime.timedelta(days=max(1, int(interval_days)))),
        "source_event_id": source_event_id,
        "synthetic": False,
    }
    with _lock:
        existing = next((item for item in _memory_records if item["event_id"] == event_id), None)
        if existing:
            return existing.copy()
        _memory_records.append(record)
        _unsynced_ids.add(event_id)
    return record.copy()


def schedule_after_mastery(
    source_event_id: str,
    learner_id: str,
    learner_code: str,
    class_level: str,
    topic: str,
) -> dict:
    previous, _ = topic_status(learner_id, class_level, topic)
    interval = _LAPSE_INTERVAL_DAYS if previous and previous.get("outcome") == "lapse" else _INITIAL_INTERVAL_DAYS
    outcome = "recovered" if previous and previous.get("outcome") == "lapse" else "scheduled"
    return _stage(
        source_event_id=source_event_id,
        learner_id=learner_id,
        learner_code=learner_code,
        class_level=class_level,
        topic=topic,
        outcome=outcome,
        interval_days=interval,
    )


def record_review_result(
    source_event_id: str,
    learner_id: str,
    learner_code: str,
    class_level: str,
    topic: str,
    correct: bool,
) -> dict:
    current, _ = topic_status(learner_id, class_level, topic)
    current_interval = int((current or {}).get("interval_days") or _INITIAL_INTERVAL_DAYS)
    interval = _next_success_interval(current_interval) if correct else _LAPSE_INTERVAL_DAYS
    return _stage(
        source_event_id=source_event_id,
        learner_id=learner_id,
        learner_code=learner_code,
        class_level=class_level,
        topic=topic,
        outcome="retained" if correct else "lapse",
        interval_days=interval,
    )


def persist_event(event_id: str) -> bool:
    with _lock:
        record = next((item.copy() for item in _memory_records if item["event_id"] == event_id), None)
        needs_sync = event_id in _unsynced_ids
    if not record or not needs_sync:
        return True
    if not _sheet_configured():
        return False
    try:
        _get_worksheet().append_row([
            record["timestamp"], record["event_id"], record["learner_id"], record["learner_code"],
            record["class_level"], record["topic"], record["outcome"], record["interval_days"],
            record["next_review_at"], record["source_event_id"],
        ])
        with _lock:
            _unsynced_ids.discard(event_id)
        return True
    except Exception as exc:
        print(f"[retention_progress] WARNING: failed to save retention event: {type(exc).__name__}")
        return False


def learner_retention_summary(learner_id: str, class_level: str, *, now: datetime.datetime | None = None) -> dict:
    from mastery_progress import get_records as get_mastery_records, summarise_topics

    now = now or _now_dt()
    mastery_records, mastery_synced = get_mastery_records(learner_id)
    mastery_records = [item for item in mastery_records if item.get("class_level") == class_level]
    mastery_topics = summarise_topics(mastery_records)
    retention_records, retention_synced = get_records(learner_id)
    retention_topics = {
        item.get("topic") for item in retention_records
        if item.get("class_level") == class_level and item.get("topic")
    }
    topics = sorted({item["topic"] for item in mastery_topics if item.get("state") == "mastered"} | retention_topics)

    rows = []
    for topic in topics:
        status, _ = topic_status(learner_id, class_level, topic)
        if not status:
            continue
        next_review = _parse(status.get("next_review_at", ""))
        due = bool(next_review and next_review <= now and status.get("outcome") != "lapse")
        days_until = None
        if next_review:
            seconds = (next_review - now).total_seconds()
            days_until = int(seconds // 86400) if seconds >= 0 else -int(abs(seconds) // 86400)
        rows.append({
            "topic": topic,
            "outcome": status.get("outcome"),
            "interval_days": int(status.get("interval_days") or _INITIAL_INTERVAL_DAYS),
            "next_review_at": status.get("next_review_at"),
            "due": due,
            "days_until_review": days_until,
            "synthetic": bool(status.get("synthetic")),
        })

    due_rows = [item for item in rows if item["due"]]
    due_rows.sort(key=lambda item: (item.get("next_review_at") or "", item["topic"]))
    upcoming = [item for item in rows if not item["due"] and item.get("outcome") != "lapse"]
    upcoming.sort(key=lambda item: (item.get("next_review_at") or "", item["topic"]))
    lapses = [item for item in rows if item.get("outcome") == "lapse"]
    return {
        "class_level": class_level,
        "topics": rows,
        "due_topics": [item["topic"] for item in due_rows],
        "next_due_topic": due_rows[0]["topic"] if due_rows else None,
        "upcoming_topics": [item["topic"] for item in upcoming],
        "retention_lapse_topics": [item["topic"] for item in lapses],
        "storage_synced": mastery_synced and retention_synced,
    }


def reset_for_tests() -> None:
    global _client, _worksheet
    with _lock:
        _memory_records.clear()
        _unsynced_ids.clear()
    _client = None
    _worksheet = None
