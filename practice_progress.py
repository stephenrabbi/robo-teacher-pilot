"""Durable, pseudonymous Practice Mode progress stored in Google Sheets."""

import datetime
import json
import os
import threading

import gspread
from practice import CLASS_TOPICS


_HEADER = [
    "Timestamp (UTC)", "Session ID", "Learner ID", "Topic", "Difficulty",
    "Score", "Questions", "Percentage", "Class Level",
]
_client = None
_worksheet = None
_memory_records: list[dict] = []
_unsynced_ids: set[str] = set()
_lock = threading.Lock()


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
            _worksheet = spreadsheet.worksheet("Practice Progress")
            headings = _worksheet.row_values(1)
            if "Class Level" not in headings:
                _worksheet.update_cell(1, len(_HEADER), "Class Level")
        except gspread.WorksheetNotFound:
            _worksheet = spreadsheet.add_worksheet(
                title="Practice Progress", rows=2000, cols=len(_HEADER)
            )
            _worksheet.append_row(_HEADER)
    return _worksheet


def save_result(learner_id: str, summary: dict) -> bool:
    """Save one completed session. Returns False if durable storage is unavailable."""
    record = {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
        "session_id": summary["session_id"],
        "learner_id": learner_id,
        "topic": summary["topic"],
        "difficulty": summary["difficulty"],
        "score": int(summary["score"]),
        "attempted": int(summary["attempted"]),
        "percentage": int(summary["percentage"]),
        "class_level": summary.get("class_level", "JSS2"),
    }
    with _lock:
        if not any(item["session_id"] == record["session_id"] for item in _memory_records):
            _memory_records.append(record)
    if not _sheet_configured():
        _unsynced_ids.add(record["session_id"])
        return False
    try:
        _get_worksheet().append_row([
            record["timestamp"], record["session_id"], learner_id, record["topic"],
            record["difficulty"], record["score"], record["attempted"], record["percentage"],
            record["class_level"],
        ])
        _unsynced_ids.discard(record["session_id"])
        return True
    except Exception as exc:
        _unsynced_ids.add(record["session_id"])
        print(f"[practice_progress] WARNING: failed to save progress: {type(exc).__name__}")
        return False


def _sheet_records(learner_id: str) -> list[dict]:
    rows = _get_worksheet().get_all_records()
    records = []
    for row in rows:
        if str(row.get("Learner ID", "")) != learner_id:
            continue
        try:
            records.append({
                "timestamp": str(row.get("Timestamp (UTC)", "")),
                "session_id": str(row.get("Session ID", "")),
                "learner_id": learner_id,
                "topic": str(row["Topic"]),
                "difficulty": str(row["Difficulty"]),
                "score": int(row["Score"]),
                "attempted": int(row["Questions"]),
                "percentage": int(row["Percentage"]),
                "class_level": str(row.get("Class Level", "JSS2") or "JSS2"),
            })
        except (KeyError, TypeError, ValueError):
            continue
    return records


def get_records(learner_id: str) -> tuple[list[dict], bool]:
    """Return learner-owned records and whether durable storage was reached."""
    if _sheet_configured():
        try:
            sheet_items = _sheet_records(learner_id)
            known_ids = {item["session_id"] for item in sheet_items}
            with _lock:
                pending = [
                    item.copy() for item in _memory_records
                    if item["learner_id"] == learner_id and item["session_id"] not in known_ids
                ]
            learner_unsynced = any(item["session_id"] in _unsynced_ids for item in pending)
            return sheet_items + pending, not learner_unsynced
        except Exception as exc:
            print(f"[practice_progress] WARNING: failed to load progress: {type(exc).__name__}")
    with _lock:
        return [item.copy() for item in _memory_records if item["learner_id"] == learner_id], False


def get_all_records() -> tuple[list[dict], bool]:
    """Load aggregate source data without returning identities to the caller."""
    if _sheet_configured():
        try:
            rows = _get_worksheet().get_all_records()
            learner_ids = {str(row.get("Learner ID", "")) for row in rows if row.get("Learner ID")}
            combined = []
            for learner_id in learner_ids:
                combined.extend(_sheet_records(learner_id))
            known = {item["session_id"] for item in combined}
            combined.extend(item.copy() for item in _memory_records if item["session_id"] not in known)
            return combined, True
        except Exception as exc:
            print(f"[practice_progress] WARNING: failed to load aggregate progress: {type(exc).__name__}")
    with _lock:
        return [item.copy() for item in _memory_records], False


def build_teacher_dashboard(class_level: str = "JSS2") -> dict:
    records, synced = get_all_records()
    class_level = class_level if class_level in CLASS_TOPICS else "JSS2"
    records = [item for item in records if item.get("class_level", "JSS2") == class_level]
    learners = {item["learner_id"] for item in records}
    attempted = sum(item["attempted"] for item in records)
    correct = sum(item["score"] for item in records)
    topics = []
    for topic in CLASS_TOPICS[class_level]:
        items = [item for item in records if item["topic"] == topic]
        questions = sum(item["attempted"] for item in items)
        if questions:
            topics.append({"topic": topic, "sessions": len(items), "questions": questions, "percentage": round(sum(item["score"] for item in items) / questions * 100)})
    topics.sort(key=lambda item: (item["percentage"], item["topic"]))
    return {
        "class_level": class_level, "learners": len(learners), "sessions": len(records),
        "questions": attempted, "average_percentage": round(correct / attempted * 100) if attempted else 0,
        "focus_topic": topics[0]["topic"] if topics else None, "topics": topics,
        "storage_synced": synced,
    }


def build_dashboard(learner_id: str, class_level: str = "JSS2") -> dict:
    records, synced = get_records(learner_id)
    class_level = class_level if class_level in CLASS_TOPICS else "JSS2"
    records = [item for item in records if item.get("class_level", "JSS2") == class_level]
    records.sort(key=lambda item: item["timestamp"], reverse=True)
    total_questions = sum(item["attempted"] for item in records)
    total_correct = sum(item["score"] for item in records)
    average = round(total_correct / total_questions * 100) if total_questions else 0

    topic_rows = []
    for topic in sorted({item["topic"] for item in records}):
        topic_records = [item for item in records if item["topic"] == topic]
        attempted = sum(item["attempted"] for item in topic_records)
        correct = sum(item["score"] for item in topic_records)
        topic_rows.append({
            "topic": topic,
            "sessions": len(topic_records),
            "correct": correct,
            "attempted": attempted,
            "percentage": round(correct / attempted * 100) if attempted else 0,
        })
    topic_rows.sort(key=lambda item: (-item["percentage"], item["topic"]))

    strongest = topic_rows[0] if topic_rows else None
    weakest = min(topic_rows, key=lambda item: (item["percentage"], item["topic"])) if topic_rows else None
    recommended_topic = weakest["topic"] if weakest else CLASS_TOPICS[class_level][0]
    recommended_difficulty = _recommended_difficulty(records, weakest)
    recommendation = _recommendation(records, weakest, recommended_difficulty)
    weekly = _weekly_summary(records)
    return {
        "class_level": class_level,
        "sessions": len(records),
        "total_questions": total_questions,
        "total_correct": total_correct,
        "average_percentage": average,
        "strongest_topic": strongest["topic"] if strongest else None,
        "focus_topic": weakest["topic"] if weakest else None,
        "topics": topic_rows,
        "recent_sessions": records[:5],
        "recommendation": recommendation,
        "recommended_topic": recommended_topic,
        "recommended_difficulty": recommended_difficulty,
        "weekly_summary": weekly,
        "storage_synced": synced,
    }


def _recommendation(records: list[dict], weakest: dict | None, difficulty: str) -> str:
    if not records:
        return "Complete your first practice session to receive a personal recommendation."
    if weakest["percentage"] < 50:
        return f"Focus on {weakest['topic']} at {difficulty} level and review each worked explanation."
    if weakest["percentage"] < 80:
        return f"Practise {weakest['topic']} again at the same level to build consistency."
    latest = records[0]
    next_level = {"Easy": "Medium", "Medium": "Challenge", "Challenge": "Challenge"}[latest["difficulty"]]
    if latest["difficulty"] == "Challenge":
        return f"Keep sharpening {latest['topic']} at Challenge level or choose a new topic."
    return f"You are ready to try {latest['topic']} at {next_level} level."


def _recommended_difficulty(records: list[dict], weakest: dict | None) -> str:
    if not records:
        return "Easy"
    matching = [item for item in records if item["topic"] == weakest["topic"]]
    current = matching[0]["difficulty"] if matching else records[0]["difficulty"]
    levels = ["Easy", "Medium", "Challenge"]
    recent = matching[:2]
    if len(recent) >= 2 and all(item["percentage"] >= 80 for item in recent):
        return levels[min(levels.index(current) + 1, 2)]
    if len(recent) >= 2 and all(item["percentage"] < 50 for item in recent):
        return levels[max(levels.index(current) - 1, 0)]
    return current


def _weekly_summary(records: list[dict]) -> dict:
    now = datetime.datetime.now(datetime.UTC)
    current_start = now - datetime.timedelta(days=7)
    previous_start = now - datetime.timedelta(days=14)

    def parsed(item):
        try: return datetime.datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
        except (ValueError, TypeError): return None

    current = [item for item in records if parsed(item) and parsed(item) >= current_start]
    previous = [item for item in records if parsed(item) and previous_start <= parsed(item) < current_start]
    attempted = sum(item["attempted"] for item in current)
    correct = sum(item["score"] for item in current)
    score = round(correct / attempted * 100) if attempted else 0
    old_attempted = sum(item["attempted"] for item in previous)
    old_score = round(sum(item["score"] for item in previous) / old_attempted * 100) if old_attempted else None
    improvement = score - old_score if old_score is not None and attempted else None
    return {
        "sessions": len(current), "questions": attempted, "percentage": score,
        "improvement_points": improvement,
    }


def _reset_for_tests() -> None:
    global _worksheet, _client
    with _lock:
        _memory_records.clear()
        _unsynced_ids.clear()
    _worksheet = None
    _client = None
