"""Choose one next-best learning action from durable learner evidence."""

from curriculum import CLASS_TOPICS, TOPIC_TERM
from mastery_progress import learner_summary
from practice_progress import build_dashboard

_ACTION_COPY = {
    "reteach": ("Reteach before moving on", "This topic still needs support, so Robo-Teacher should explain it differently before checking again.", "Reteach this topic →"),
    "review": ("Refresh an older topic", "You learned this before, but a short retrieval review will help keep it strong.", "Review now →"),
    "mastery_check": ("Confirm mastery", "Your recent check was promising, but there is not enough evidence yet to move on confidently.", "Check my mastery →"),
    "practice": ("Strengthen with practice", "A short personalised practice is the best next step before Robo-Teacher changes topic or difficulty.", "Start practice →"),
    "advance": ("Move to the next topic", "Your current evidence is strong enough for Robo-Teacher to continue along the curriculum path.", "Learn the next topic →"),
}


def _topic_rows(practice):
    return {item["topic"]: item for item in practice.get("topics", []) if item.get("topic")}


def _mastery_rows(mastery):
    return {item["topic"]: item for item in mastery.get("topics", []) if item.get("topic")}


def _latest_topic(topic_names, rows):
    candidates = [rows[name] for name in topic_names if name in rows]
    return max(candidates, key=lambda item: item.get("last_seen", ""))["topic"] if candidates else None


def _next_unmastered(class_level, mastered, preferred=None):
    topics = list(CLASS_TOPICS[class_level])
    if preferred in topics and preferred not in mastered:
        return preferred
    indexes = [topics.index(topic) for topic in mastered if topic in topics]
    start = max(indexes) + 1 if indexes else 0
    ordered = topics[start:] + topics[:start]
    return next((topic for topic in ordered if topic not in mastered), topics[0])


def _make_plan(action, topic, class_level, practice, mastery, reason_code):
    title, reason, button = _ACTION_COPY[action]
    difficulty = practice.get("recommended_difficulty") or "Easy"
    row = _topic_rows(practice).get(topic, {})
    if action == "reteach" and row.get("mastery_status") == "needs_support":
        difficulty = "Easy"
    prompts = {
        "reteach": f"Reteach me {topic} at {class_level} level using a different simple approach, then pause so I can check my understanding.",
        "review": f"Give me a short retrieval review of {topic} at {class_level} level, then pause for a quick understanding check.",
        "mastery_check": f"Give me a very short recap of {topic} at {class_level} level, then pause so Robo-Teacher can check whether I have mastered it.",
        "advance": f"Teach me {topic} step by step at {class_level} level.",
        "practice": "",
    }
    return {
        "action": action,
        "topic": topic,
        "term": TOPIC_TERM[class_level][topic],
        "difficulty": difficulty,
        "title": title,
        "reason": reason,
        "button_text": button,
        "reason_code": reason_code,
        "prompt": prompts[action],
        "has_history": bool(practice.get("sessions") or mastery.get("topics")),
        "mastered_topics": sorted(set(mastery.get("mastered_topics", []))),
        "needs_support_topics": sorted(set(mastery.get("needs_support_topics", []))),
        "storage_synced": bool(practice.get("storage_synced")) and bool(mastery.get("storage_synced")),
    }


def choose_next_action(class_level, practice, mastery):
    """Return one conservative next action without mutating learner evidence."""
    class_level = class_level if class_level in CLASS_TOPICS else "JSS2"
    topics = list(CLASS_TOPICS[class_level])
    practice_rows = _topic_rows(practice)
    mastery_rows = _mastery_rows(mastery)
    persistent_mastered = {t for t, row in mastery_rows.items() if row.get("state") == "mastered"}
    practice_mastered = {t for t, row in practice_rows.items() if row.get("mastery_status") == "mastered"}
    mastered = persistent_mastered | practice_mastered

    support_topic = _latest_topic([t for t in mastery.get("needs_support_topics", []) if t in topics], mastery_rows)
    if support_topic:
        return _make_plan("reteach", support_topic, class_level, practice, mastery, "persistent_needs_support")

    practice_support = [row for row in practice_rows.values() if row.get("mastery_status") == "needs_support" and row.get("topic") not in persistent_mastered]
    if practice_support:
        weakest = min(practice_support, key=lambda row: (row.get("mastery_estimate", 100), -row.get("evidence_questions", 0), topics.index(row["topic"])))
        return _make_plan("reteach", weakest["topic"], class_level, practice, mastery, "practice_needs_support")

    due = [row for row in practice_rows.values() if row.get("due_for_review") and row.get("topic") in topics]
    if due:
        oldest = max(due, key=lambda row: (row.get("days_since_practice") or 0, -topics.index(row["topic"])))
        return _make_plan("review", oldest["topic"], class_level, practice, mastery, "spaced_review_due")

    developing_topic = _latest_topic([t for t in mastery.get("developing_topics", []) if t in topics and t not in practice_mastered], mastery_rows)
    if developing_topic:
        return _make_plan("mastery_check", developing_topic, class_level, practice, mastery, "persistent_developing")

    practice_developing = [row for row in practice_rows.values() if row.get("mastery_status") == "developing" and row.get("topic") not in persistent_mastered]
    if practice_developing:
        weakest = min(practice_developing, key=lambda row: (row.get("mastery_estimate", 100), -row.get("evidence_questions", 0), topics.index(row["topic"])))
        return _make_plan("practice", weakest["topic"], class_level, practice, mastery, "practice_developing")

    target = _next_unmastered(class_level, mastered, practice.get("recommended_topic"))
    has_history = bool(practice.get("sessions") or mastery.get("topics"))
    return _make_plan("advance" if has_history else "practice", target, class_level, practice, mastery, "next_curriculum_topic" if has_history else "establish_baseline")


def build_autonomous_plan(learner_id, class_level):
    class_level = class_level if class_level in CLASS_TOPICS else "JSS2"
    return choose_next_action(class_level, build_dashboard(learner_id, class_level), learner_summary(learner_id, class_level))
