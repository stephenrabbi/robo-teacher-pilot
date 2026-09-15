"""Derive current teacher-support escalation from existing mastery evidence.

No extra learner content is persisted here. Escalation is computed from the
same pseudonymous mastery events already stored by Robo-Teacher and clears
when later mastery resolves the topic.
"""

from __future__ import annotations

from collections import Counter

from mastery_progress import get_records
from misconceptions import misconception_label


def _unresolved_segment(items: list[dict]) -> list[dict]:
    ordered = sorted(items, key=lambda item: item.get("timestamp", ""))
    if not ordered or ordered[-1].get("state") != "needs_support":
        return []
    last_mastered = -1
    for index, item in enumerate(ordered):
        if item.get("state") == "mastered":
            last_mastered = index
    return ordered[last_mastered + 1 :]


def topic_intervention(items: list[dict]) -> dict:
    segment = _unresolved_segment(items)
    if not segment:
        return {
            "level": "none",
            "reason": None,
            "incorrect_checks": 0,
            "failed_reteaches": 0,
            "recurring_misconception": None,
        }

    incorrect = [item for item in segment if not item.get("correct")]
    failed_reteaches = [item for item in incorrect if item.get("stage") == "reteach"]
    categories = Counter(item.get("misconception") for item in incorrect if item.get("misconception"))
    recurring_category, recurring_count = categories.most_common(1)[0] if categories else (None, 0)

    level = "none"
    reason = None
    if len(failed_reteaches) >= 2:
        level = "teacher_support"
        reason = "Robo-Teacher has already reteached this topic more than once without secure mastery."
    elif len(incorrect) >= 4:
        level = "teacher_support"
        reason = "Several recent checks remain unresolved despite personalised support."
    elif recurring_count >= 3:
        level = "teacher_support"
        reason = "The same misconception has remained unresolved across several checks."
    elif failed_reteaches or len(incorrect) >= 2:
        level = "watch"
        reason = "Recent evidence shows this topic still needs close monitoring."

    return {
        "level": level,
        "reason": reason,
        "incorrect_checks": len(incorrect),
        "failed_reteaches": len(failed_reteaches),
        "recurring_misconception": misconception_label(recurring_category),
    }


def learner_intervention_summary(learner_id: str, class_level: str) -> dict:
    records, synced = get_records(learner_id)
    records = [item for item in records if item.get("class_level") == class_level]
    topics = []
    for topic in sorted({item.get("topic") for item in records if item.get("topic")}):
        result = topic_intervention([item for item in records if item.get("topic") == topic])
        if result["level"] == "none":
            continue
        topics.append({"topic": topic, **result})
    topics.sort(key=lambda item: (item["level"] != "teacher_support", -item["failed_reteaches"], -item["incorrect_checks"], item["topic"]))
    urgent = [item for item in topics if item["level"] == "teacher_support"]
    watch = [item for item in topics if item["level"] == "watch"]
    return {
        "teacher_support_required": bool(urgent),
        "teacher_support_topics": [item["topic"] for item in urgent],
        "watch_topics": [item["topic"] for item in watch],
        "interventions": topics,
        "teacher_support_focus": urgent[0] if urgent else None,
        "storage_synced": synced,
    }


def teacher_intervention_summary(class_level: str) -> dict:
    records, synced = get_records(None)
    records = [item for item in records if item.get("class_level") == class_level]
    learner_ids = sorted({item.get("learner_id") for item in records if item.get("learner_id")})
    learners = []
    for learner_id in learner_ids:
        items = [item for item in records if item.get("learner_id") == learner_id]
        latest_code = next((item.get("learner_code") for item in reversed(sorted(items, key=lambda x: x.get("timestamp", ""))) if item.get("learner_code")), "Unassigned")
        summary = learner_intervention_summary(learner_id, class_level)
        if not summary["interventions"]:
            continue
        learners.append({
            "learner_code": latest_code,
            "teacher_support_required": summary["teacher_support_required"],
            "teacher_support_topics": summary["teacher_support_topics"],
            "watch_topics": summary["watch_topics"],
            "teacher_support_focus": summary["teacher_support_focus"],
        })
    urgent = [item for item in learners if item["teacher_support_required"]]
    return {
        "teacher_support_count": len(urgent),
        "teacher_support_learners": urgent,
        "intervention_learners": learners,
        "storage_synced": synced,
    }
