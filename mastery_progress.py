"""Durable, pseudonymous mastery evidence for Check Understanding."""

import datetime
import json
import os
import re
import threading

import gspread
from curriculum import CLASS_TOPICS
from misconceptions import misconception_label, strategy_options

_HEADER = [
    "Timestamp (UTC)", "Event ID", "Learner ID", "Learner Code",
    "Class Level", "Topic", "Stage", "Correct", "State",
    "Misconception", "Teaching Strategy", "Applied Misconception",
    "Applied Strategy", "Strategy Outcome",
]
_client = None
_worksheet = None
_memory_records: list[dict] = []
_unsynced_ids: set[str] = set()
_lock = threading.Lock()

_TOPIC_ALIASES = {
    "Whole Numbers": ("whole number", "place value", "number line"),
    "Factors, Multiples, LCM & HCF": ("factor", "multiple", "lcm", "hcf", "highest common factor", "lowest common multiple"),
    "Fractions": ("fraction", "numerator", "denominator", "mixed number"),
    "Estimation": ("estimate", "estimation", "round off", "rounding"),
    "Decimals & Approximation": ("decimal", "approximation", "significant figure", "decimal place"),
    "Number Bases (Binary)": ("binary", "base two", "base 2"),
    "Positive & Negative Integers": ("negative integer", "positive integer", "directed number"),
    "Introductory Algebra": ("algebra", "algebraic expression", "variable", "unknown"),
    "Simple Equations": ("simple equation", "solve for x", "linear equation", "equation"),
    "Plane Shapes & Mensuration": ("plane shape", "perimeter", "area", "mensuration"),
    "3D Shapes & Volume": ("3d shape", "three dimensional", "volume", "cuboid", "cube"),
    "Angles & Construction": ("angle", "construction", "bisect"),
    "Data Presentation": ("bar chart", "frequency table", "data presentation", "graph of data"),
    "Mean, Median & Mode": ("mean", "median", "mode", "average"),
    "Standard Form": ("standard form", "scientific notation"),
    "Prime Factors, Squares & Roots": ("prime factor", "square root", "square number", "root"),
    "Fractions, Ratios, Decimals & Percentages": ("fraction", "ratio", "decimal", "percentage", "percent"),
    "Commercial Arithmetic": ("profit", "loss", "discount", "simple interest", "commercial arithmetic"),
    "Approximation": ("approximation", "significant figure", "decimal place", "rounding"),
    "Directed Numbers": ("directed number", "negative number", "positive number", "integer"),
    "Algebraic Expressions & Factorisation": ("algebraic expression", "factorise", "factorize", "expansion", "expand bracket"),
    "Algebraic Fractions": ("algebraic fraction", "fractional expression"),
    "Linear Inequalities": ("inequality", "greater than", "less than"),
    "Linear Graphs": ("linear graph", "gradient", "slope", "coordinate graph"),
    "Plane Shapes & Scale Drawing": ("scale drawing", "plane shape", "scale factor"),
    "Angles & Polygons": ("polygon", "interior angle", "exterior angle"),
    "Elevation & Depression": ("elevation", "depression"),
    "Bearings & Distances": ("bearing", "distance"),
    "Pythagoras & Mensuration": ("pythagoras", "pythagorean", "hypotenuse", "mensuration"),
    "Statistics & Data Presentation": ("statistics", "frequency", "bar chart", "histogram", "data presentation"),
    "Probability": ("probability", "chance", "outcome", "sample space"),
    "Number Bases": ("number base", "base ten", "base 10", "base conversion"),
    "Rational & Irrational Numbers": ("rational", "irrational", "surds"),
    "Ratio, Proportion & Variation": ("ratio", "proportion", "variation", "direct variation", "inverse variation"),
    "Factorisation & Quadratic Expressions": ("quadratic", "factorisation", "factorization", "factorise", "factorize"),
    "Formulae & Change of Subject": ("change of subject", "make the subject", "formula", "formulae"),
    "Equations Involving Fractions": ("equation involving fraction", "fraction equation", "fractional equation"),
    "Simultaneous Equations": ("simultaneous equation", "elimination method", "substitution method"),
    "Similar Shapes": ("similar shape", "similarity", "enlargement"),
    "Trigonometry": ("trigonometry", "sine", "cosine", "tangent", "sin ", "cos ", "tan "),
    "Geometry & Construction": ("geometry", "construction", "locus"),
    "Mensuration & Volumes": ("mensuration", "volume", "surface area", "cylinder", "cone", "sphere"),
    "Statistics & Averages": ("statistics", "mean", "median", "mode", "average"),
    "Pie Charts": ("pie chart", "sector angle"),
}


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
            _worksheet = spreadsheet.worksheet("Mastery Memory")
            headings = _worksheet.row_values(1)
            for column_index, heading in enumerate(_HEADER, start=1):
                if heading in headings:
                    continue
                current_columns = getattr(_worksheet, "col_count", len(headings))
                if current_columns < column_index:
                    _worksheet.add_cols(column_index - current_columns)
                _worksheet.update_cell(1, column_index, heading)
        except gspread.WorksheetNotFound:
            _worksheet = spreadsheet.add_worksheet(title="Mastery Memory", rows=3000, cols=len(_HEADER))
            _worksheet.append_row(_HEADER)
    return _worksheet


def infer_topic(text: str, class_level: str, topic_hint: str = "") -> str | None:
    """Infer a curriculum topic conservatively from lesson text, with a validated hint fallback."""
    topics = CLASS_TOPICS.get(class_level, CLASS_TOPICS["JSS2"])
    hint = topic_hint.strip()
    source = re.sub(r"\s+", " ", (text or "").lower())
    scored: list[tuple[int, int, str]] = []
    for topic in topics:
        score = 0
        phrase = topic.lower()
        if phrase in source:
            score += 12
        for alias in _TOPIC_ALIASES.get(topic, ()):
            if alias in source:
                score += 4 + min(3, len(alias.split()))
        words = [word for word in re.findall(r"[a-z0-9]+", phrase) if len(word) > 3 and word not in {"numbers", "shapes", "data"}]
        overlap = sum(1 for word in words if re.search(rf"\b{re.escape(word)}\b", source))
        score += overlap
        if score:
            scored.append((score, overlap, topic))
    if scored:
        scored.sort(reverse=True)
        best = scored[0]
        if best[0] >= 4 or best[1] >= 2:
            return best[2]
    return hint if hint in topics else None


def state_for_event(stage: str, correct: bool) -> str:
    if stage == "reteach":
        return "mastered" if correct else "needs_support"
    return "developing" if correct else "needs_support"


def stage_event(
    event_id: str,
    learner_id: str,
    learner_code: str,
    class_level: str,
    topic: str,
    stage: str,
    correct: bool,
    misconception: str = "",
    teaching_strategy: str = "",
    applied_misconception: str = "",
    applied_strategy: str = "",
) -> dict:
    strategy_outcome = ""
    if stage == "reteach" and applied_strategy:
        strategy_outcome = "success" if correct else "failure"
    record = {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
        "event_id": event_id,
        "learner_id": learner_id,
        "learner_code": learner_code.strip().upper(),
        "class_level": class_level,
        "topic": topic,
        "stage": stage,
        "correct": bool(correct),
        "state": state_for_event(stage, bool(correct)),
        "misconception": misconception if not correct else "",
        "teaching_strategy": teaching_strategy if not correct else "",
        "applied_misconception": applied_misconception if applied_strategy else "",
        "applied_strategy": applied_strategy,
        "strategy_outcome": strategy_outcome,
    }
    with _lock:
        existing = next((item for item in _memory_records if item["event_id"] == event_id), None)
        if existing:
            return existing.copy()
        _memory_records.append(record)
        _unsynced_ids.add(event_id)
    return record.copy()


def persist_event(event_id: str) -> bool:
    with _lock:
        record = next((item.copy() for item in _memory_records if item["event_id"] == event_id), None)
    if not record or event_id not in _unsynced_ids:
        return True
    if not _sheet_configured():
        return False
    try:
        _get_worksheet().append_row([
            record["timestamp"], record["event_id"], record["learner_id"], record["learner_code"],
            record["class_level"], record["topic"], record["stage"], "TRUE" if record["correct"] else "FALSE", record["state"],
            record.get("misconception", ""), record.get("teaching_strategy", ""),
            record.get("applied_misconception", ""), record.get("applied_strategy", ""), record.get("strategy_outcome", ""),
        ])
        with _lock:
            _unsynced_ids.discard(event_id)
        return True
    except Exception as exc:
        print(f"[mastery_progress] WARNING: failed to save mastery event: {type(exc).__name__}")
        return False


def _row_to_record(row: dict) -> dict | None:
    try:
        value = str(row.get("Correct", "")).strip().lower()
        correct = value in {"true", "1", "yes"}
        stage = str(row.get("Stage", "initial")) or "initial"
        return {
            "timestamp": str(row.get("Timestamp (UTC)", "")),
            "event_id": str(row.get("Event ID", "")),
            "learner_id": str(row.get("Learner ID", "")),
            "learner_code": str(row.get("Learner Code", "")).strip().upper(),
            "class_level": str(row.get("Class Level", "JSS2") or "JSS2"),
            "topic": str(row.get("Topic", "")),
            "stage": stage,
            "correct": correct,
            "state": str(row.get("State", "")) or state_for_event(stage, correct),
            "misconception": str(row.get("Misconception", "") or ""),
            "teaching_strategy": str(row.get("Teaching Strategy", "") or ""),
            "applied_misconception": str(row.get("Applied Misconception", "") or ""),
            "applied_strategy": str(row.get("Applied Strategy", "") or ""),
            "strategy_outcome": str(row.get("Strategy Outcome", "") or ""),
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
            print(f"[mastery_progress] WARNING: failed to load mastery memory: {type(exc).__name__}")
    known = {item["event_id"] for item in records}
    with _lock:
        pending = [item.copy() for item in _memory_records if item["event_id"] not in known and (learner_id is None or item["learner_id"] == learner_id)]
        pending_unsynced = any(item["event_id"] in _unsynced_ids for item in pending)
    return records + pending, synced and not pending_unsynced


def _strategy_effectiveness(items: list[dict], misconception: str) -> dict:
    options = list(strategy_options(misconception))
    counts = {strategy: {"strategy": strategy, "successes": 0, "failures": 0, "attempts": 0} for strategy in options}
    for item in items:
        if item.get("applied_misconception") != misconception:
            continue
        strategy = item.get("applied_strategy", "")
        outcome = item.get("strategy_outcome", "")
        if strategy not in counts or outcome not in {"success", "failure"}:
            continue
        counts[strategy]["attempts"] += 1
        counts[strategy]["successes"] += int(outcome == "success")
        counts[strategy]["failures"] += int(outcome == "failure")

    evidence = [counts[strategy] for strategy in options if counts[strategy]["attempts"]]
    successful = [row for row in evidence if row["successes"]]
    if successful:
        selected = max(
            successful,
            key=lambda row: (
                row["successes"] / row["attempts"],
                row["successes"],
                -row["failures"],
                -options.index(row["strategy"]),
            ),
        )["strategy"]
        reason = "worked_before"
    else:
        tried = {row["strategy"] for row in evidence}
        selected = next((strategy for strategy in options if strategy not in tried), None)
        if selected:
            reason = "new_after_failure" if tried else "default"
        elif options:
            selected = min(
                options,
                key=lambda strategy: (
                    counts[strategy]["failures"],
                    counts[strategy]["attempts"],
                    options.index(strategy),
                ),
            )
            reason = "least_failed"
        else:
            selected = None
            reason = "none"
    return {
        "preferred_strategy": selected,
        "selection_reason": reason,
        "evidence": evidence,
        "successful_strategies": [row["strategy"] for row in successful],
        "failed_strategies": [row["strategy"] for row in evidence if row["failures"] and not row["successes"]],
    }


def summarise_topics(records: list[dict]) -> list[dict]:
    topics = []
    for topic in sorted({item["topic"] for item in records if item.get("topic")}):
        items = sorted((item for item in records if item["topic"] == topic), key=lambda item: item.get("timestamp", ""))
        latest = items[-1]
        attempts = len(items)
        correct = sum(1 for item in items if item.get("correct"))
        reteach_attempts = sum(1 for item in items if item.get("stage") == "reteach")
        confidence = "high" if attempts >= 4 else "medium" if attempts >= 2 else "low"
        misconception = latest.get("misconception", "") if latest.get("state") == "needs_support" else ""
        effectiveness = _strategy_effectiveness(items, misconception) if misconception else None
        strategy = effectiveness.get("preferred_strategy") if effectiveness else None
        topics.append({
            "topic": topic,
            "state": latest.get("state", "developing"),
            "confidence": confidence,
            "checks": attempts,
            "correct_checks": correct,
            "reteach_checks": reteach_attempts,
            "last_seen": latest.get("timestamp", ""),
            "misconception": misconception or None,
            "misconception_label": misconception_label(misconception),
            "teaching_strategy": strategy,
            "strategy_effectiveness": effectiveness,
        })
    topics.sort(key=lambda item: (item["state"] != "needs_support", item["last_seen"]), reverse=False)
    return topics


def learner_summary(learner_id: str, class_level: str) -> dict:
    records, synced = get_records(learner_id)
    records = [item for item in records if item.get("class_level") == class_level]
    topics = summarise_topics(records)
    support = [item for item in topics if item["state"] == "needs_support"]
    developing = [item for item in topics if item["state"] == "developing"]
    mastered = [item for item in topics if item["state"] == "mastered"]
    focus = (max(support, key=lambda item: item["last_seen"]) if support else max(developing, key=lambda item: item["last_seen"]) if developing else None)
    misconception_focus = None
    if focus and focus.get("misconception"):
        misconception_focus = {
            "topic": focus["topic"],
            "category": focus["misconception"],
            "label": focus.get("misconception_label"),
            "teaching_tip": focus.get("teaching_strategy"),
            "strategy_effectiveness": focus.get("strategy_effectiveness"),
        }
    return {
        "class_level": class_level,
        "topics": topics,
        "mastered_topics": [item["topic"] for item in mastered],
        "developing_topics": [item["topic"] for item in developing],
        "needs_support_topics": [item["topic"] for item in support],
        "focus_topic": focus["topic"] if focus else None,
        "misconception_focus": misconception_focus,
        "storage_synced": synced,
    }


def teacher_summary(class_level: str) -> dict:
    records, synced = get_records(None)
    records = [item for item in records if item.get("class_level") == class_level]
    learners = {}
    topic_support = {}
    misconception_counts = {}
    strategy_by_misconception = {}
    effectiveness_by_misconception = {}
    topic_by_misconception = {}
    for learner_id in sorted({item["learner_id"] for item in records}):
        items = [item for item in records if item["learner_id"] == learner_id]
        topics = summarise_topics(items)
        latest_code = next((item.get("learner_code") for item in reversed(items) if item.get("learner_code")), "Unassigned")
        support_rows = [item for item in topics if item["state"] == "needs_support"]
        support = [item["topic"] for item in support_rows]
        current = support_rows[0] if support_rows else None
        learners[learner_id] = {
            "learner_code": latest_code,
            "mastered_topics": [item["topic"] for item in topics if item["state"] == "mastered"],
            "developing_topics": [item["topic"] for item in topics if item["state"] == "developing"],
            "needs_support_topics": support,
            "support_topic": current["topic"] if current else None,
            "support_misconception": current.get("misconception_label") if current else None,
            "teaching_strategy": current.get("teaching_strategy") if current else None,
            "strategy_effectiveness": current.get("strategy_effectiveness") if current else None,
        }
        for row in support_rows:
            topic_support[row["topic"]] = topic_support.get(row["topic"], 0) + 1
            category = row.get("misconception")
            if category:
                misconception_counts[category] = misconception_counts.get(category, 0) + 1
                strategy_by_misconception[category] = row.get("teaching_strategy")
                effectiveness_by_misconception[category] = row.get("strategy_effectiveness")
                topic_by_misconception[category] = row["topic"]
    focus = max(topic_support, key=lambda topic: (topic_support[topic], topic)) if topic_support else None
    misconception = max(misconception_counts, key=lambda key: (misconception_counts[key], key)) if misconception_counts else None
    return {
        "class_level": class_level,
        "learners": list(learners.values()),
        "focus_topic": focus,
        "focus_misconception": misconception_label(misconception),
        "focus_misconception_topic": topic_by_misconception.get(misconception) if misconception else None,
        "focus_teaching_strategy": strategy_by_misconception.get(misconception) if misconception else None,
        "focus_strategy_effectiveness": effectiveness_by_misconception.get(misconception) if misconception else None,
        "storage_synced": synced,
    }
