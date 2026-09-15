"""Choose one next-best learning action from durable learner evidence."""

from curriculum import CLASS_TOPICS, TOPIC_TERM
from intervention_support import learner_intervention_summary
from learning_prerequisites import direct_prerequisites
from mastery_progress import learner_summary
from practice_progress import build_dashboard
from retention_progress import learner_retention_summary

_ACTION_COPY = {
    "teacher_help": ("Teacher support recommended", "This topic has remained unresolved after repeated personalised support, so Robo-Teacher should pause and involve a teacher.", "Pause and ask my teacher →"),
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


def _retention_rows(retention):
    return {item["topic"]: item for item in (retention or {}).get("topics", []) if item.get("topic")}


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


def _evidence_state(topic, practice_rows, mastery_rows):
    """Return the strongest current evidence state for one prerequisite."""
    mastery_row = mastery_rows.get(topic, {})
    state = mastery_row.get("state")
    if state == "mastered":
        return "mastered"
    if state == "needs_support":
        return "needs_support"
    if state == "developing":
        return "developing"

    practice_row = practice_rows.get(topic, {})
    status = practice_row.get("mastery_status")
    if status == "mastered":
        return "mastered"
    if status == "needs_support":
        return "needs_support"
    if status == "developing":
        return "developing"
    return "unknown"


def _repeated_difficulty(topic, practice_rows, mastery_rows):
    mastery_row = mastery_rows.get(topic, {})
    if mastery_row.get("state") == "needs_support" and int(mastery_row.get("checks") or 0) >= 2:
        return True
    practice_row = practice_rows.get(topic, {})
    return (
        practice_row.get("mastery_status") == "needs_support"
        and int(practice_row.get("evidence_questions") or 0) >= 5
    )


def _merge_intervention(mastery: dict, intervention: dict) -> dict:
    rows = _mastery_rows(mastery)
    for item in intervention.get("interventions", []):
        row = rows.get(item.get("topic"))
        if row is not None:
            row["intervention_level"] = item.get("level", "none")
            row["intervention_reason"] = item.get("reason")
            row["failed_reteaches"] = item.get("failed_reteaches", 0)
            row["unresolved_incorrect_checks"] = item.get("incorrect_checks", 0)
    mastery["teacher_support_required"] = intervention.get("teacher_support_required", False)
    mastery["teacher_support_topics"] = intervention.get("teacher_support_topics", [])
    mastery["watch_topics"] = intervention.get("watch_topics", [])
    mastery["teacher_support_focus"] = intervention.get("teacher_support_focus")
    return mastery


def _make_plan(
    action,
    topic,
    class_level,
    practice,
    mastery,
    reason_code,
    *,
    retention=None,
    foundation_for=None,
    prerequisite_state=None,
):
    title, reason, button = _ACTION_COPY[action]
    difficulty = practice.get("recommended_difficulty") or "Easy"
    practice_row = _topic_rows(practice).get(topic, {})
    mastery_row = _mastery_rows(mastery).get(topic, {})
    retention_row = _retention_rows(retention).get(topic, {})
    misconception = mastery_row.get("misconception_label")
    teaching_strategy = mastery_row.get("teaching_strategy")
    teacher_support_reason = mastery_row.get("intervention_reason")

    if action == "teacher_help":
        reason = teacher_support_reason or reason
        if foundation_for:
            reason = f"{topic} is a foundation for {foundation_for}, but it has remained unresolved after repeated support. Pause Autopilot and involve a teacher before returning to {foundation_for}."
    elif action == "reteach" and practice_row.get("mastery_status") == "needs_support":
        difficulty = "Easy"

    if action == "reteach" and reason_code == "retention_lapse":
        title = "Refresh after a retention lapse"
        reason = (
            f"You previously mastered {topic}, but the scheduled retrieval check showed that it is becoming harder to recall. "
            "Robo-Teacher will give a short refresher, check again, and bring the next review closer."
        )
        button = "Refresh this topic →"
        difficulty = "Easy"
    elif action == "reteach" and misconception and teaching_strategy:
        reason = f"Recent checks suggest {misconception.lower()}. Robo-Teacher will change the teaching approach instead of repeating the same explanation."

    if action == "review" and retention_row:
        interval = int(retention_row.get("interval_days") or 2)
        title = "Spaced review due"
        button = "Do my quick review →"
        reason = (
            f"{topic} was retained strongly enough for a {interval}-day review interval. "
            "A short retrieval check is due now; success will lengthen the next interval, while difficulty will trigger a brief refresher."
        )

    if foundation_for and action != "teacher_help":
        if action == "reteach":
            title = "Repair a missing foundation"
            button = "Strengthen foundation →"
            reason = (
                f"{topic} supports {foundation_for}, and your saved evidence shows this foundation needs work. "
                f"Robo-Teacher will repair it first, then return to {foundation_for}."
            )
        else:
            title = "Check a prerequisite"
            button = "Check foundation →"
            reason = (
                f"Before continuing with {foundation_for}, Robo-Teacher will quickly confirm {topic}. "
                f"If the foundation is secure, the learning path returns to {foundation_for}; if not, it will be repaired first."
            )

    reteach_prompt = (
        f"Reteach me {topic} at {class_level} level using a different simple approach. "
        + (f"This is a prerequisite for {foundation_for}; after this check, return to {foundation_for} when the foundation is secure. " if foundation_for else "")
        + ("This is a retention refresher after a scheduled review lapse. Keep it short and focus on active recall. " if reason_code == "retention_lapse" else "")
        + (f"The recurring misconception is: {misconception}. Use this intervention strategy: {teaching_strategy} " if misconception and teaching_strategy else "")
        + "Do not repeat the previous explanation word for word. Use one short worked example, then pause so I can check my understanding."
    )
    mastery_prompt = (
        f"Give me a very short recap of {topic} at {class_level} level. "
        + (f"This is a prerequisite check before returning to {foundation_for}. " if foundation_for else "")
        + "Then pause so Robo-Teacher can check whether I have mastered it."
    )
    prompts = {
        "teacher_help": "",
        "reteach": reteach_prompt,
        "review": f"Give me a very short retrieval cue for {topic} at {class_level} level without giving away the answer, then pause for one quick understanding check.",
        "mastery_check": mastery_prompt,
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
        "misconception": misconception,
        "teaching_strategy": teaching_strategy,
        "teacher_support_required": action == "teacher_help",
        "teacher_support_reason": teacher_support_reason,
        "foundation_for": foundation_for,
        "prerequisite_state": prerequisite_state,
        "direct_prerequisites": list(direct_prerequisites(class_level, foundation_for or topic)),
        "retention_outcome": retention_row.get("outcome") or None,
        "retention_interval_days": retention_row.get("interval_days"),
        "next_review_at": retention_row.get("next_review_at"),
        "retention_due_topics": list((retention or {}).get("due_topics", [])),
        "has_history": bool(practice.get("sessions") or mastery.get("topics")),
        "mastered_topics": sorted(set(mastery.get("mastered_topics", []))),
        "needs_support_topics": sorted(set(mastery.get("needs_support_topics", []))),
        "storage_synced": (
            bool(practice.get("storage_synced"))
            and bool(mastery.get("storage_synced"))
            and bool((retention or {"storage_synced": True}).get("storage_synced"))
        ),
    }


def _foundation_plan(class_level, target_topic, practice, mastery, retention=None):
    """Choose a prerequisite intervention only when evidence justifies it."""
    prerequisites = direct_prerequisites(class_level, target_topic)
    if not prerequisites:
        return None

    practice_rows = _topic_rows(practice)
    mastery_rows = _mastery_rows(mastery)
    states = [(topic, _evidence_state(topic, practice_rows, mastery_rows)) for topic in prerequisites]

    for prerequisite, state in states:
        if state == "needs_support" and mastery_rows.get(prerequisite, {}).get("intervention_level") == "teacher_support":
            return _make_plan(
                "teacher_help",
                prerequisite,
                class_level,
                practice,
                mastery,
                "prerequisite_teacher_support_required",
                retention=retention,
                foundation_for=target_topic,
                prerequisite_state=state,
            )

    for prerequisite, state in states:
        if state == "needs_support":
            return _make_plan(
                "reteach",
                prerequisite,
                class_level,
                practice,
                mastery,
                "prerequisite_needs_support",
                retention=retention,
                foundation_for=target_topic,
                prerequisite_state=state,
            )

    for prerequisite, state in states:
        if state == "developing":
            return _make_plan(
                "mastery_check",
                prerequisite,
                class_level,
                practice,
                mastery,
                "prerequisite_not_secure",
                retention=retention,
                foundation_for=target_topic,
                prerequisite_state=state,
            )

    # A single wrong answer is not enough reason to backtrack into unknown
    # foundations. Repeated target difficulty earns one quick prerequisite check.
    if _repeated_difficulty(target_topic, practice_rows, mastery_rows):
        for prerequisite, state in states:
            if state == "unknown":
                return _make_plan(
                    "mastery_check",
                    prerequisite,
                    class_level,
                    practice,
                    mastery,
                    "prerequisite_check_after_repeated_difficulty",
                    retention=retention,
                    foundation_for=target_topic,
                    prerequisite_state=state,
                )
    return None


def choose_next_action(class_level, practice, mastery, retention=None):
    """Return one conservative next action without mutating learner evidence."""
    class_level = class_level if class_level in CLASS_TOPICS else "JSS2"
    retention = retention or {"topics": [], "due_topics": [], "storage_synced": True}
    topics = list(CLASS_TOPICS[class_level])
    practice_rows = _topic_rows(practice)
    mastery_rows = _mastery_rows(mastery)
    retention_rows = _retention_rows(retention)
    persistent_mastered = {t for t, row in mastery_rows.items() if row.get("state") == "mastered"}
    practice_mastered = {t for t, row in practice_rows.items() if row.get("mastery_status") == "mastered"}
    mastered = persistent_mastered | practice_mastered

    support_topic = _latest_topic([t for t in mastery.get("needs_support_topics", []) if t in topics], mastery_rows)
    if support_topic:
        support_row = mastery_rows.get(support_topic, {})
        if support_row.get("intervention_level") == "teacher_support":
            return _make_plan("teacher_help", support_topic, class_level, practice, mastery, "teacher_support_required", retention=retention)
        retention_row = retention_rows.get(support_topic, {})
        if retention_row.get("outcome") == "lapse":
            return _make_plan("reteach", support_topic, class_level, practice, mastery, "retention_lapse", retention=retention)
        foundation = _foundation_plan(class_level, support_topic, practice, mastery, retention)
        if foundation:
            return foundation
        return _make_plan("reteach", support_topic, class_level, practice, mastery, "persistent_needs_support", retention=retention)

    practice_support = [row for row in practice_rows.values() if row.get("mastery_status") == "needs_support" and row.get("topic") not in persistent_mastered]
    if practice_support:
        weakest = min(practice_support, key=lambda row: (row.get("mastery_estimate", 100), -row.get("evidence_questions", 0), topics.index(row["topic"])))
        foundation = _foundation_plan(class_level, weakest["topic"], practice, mastery, retention)
        if foundation:
            return foundation
        return _make_plan("reteach", weakest["topic"], class_level, practice, mastery, "practice_needs_support", retention=retention)

    retention_due = [retention_rows[topic] for topic in retention.get("due_topics", []) if topic in topics and topic in retention_rows]
    if retention_due:
        earliest = min(retention_due, key=lambda row: (row.get("next_review_at") or "", topics.index(row["topic"])))
        return _make_plan("review", earliest["topic"], class_level, practice, mastery, "retention_review_due", retention=retention)

    # Keep the older practice-based review signal as a fallback for topics that
    # predate retention scheduling or only have practice evidence.
    due = [row for row in practice_rows.values() if row.get("due_for_review") and row.get("topic") in topics]
    if due:
        oldest = max(due, key=lambda row: (row.get("days_since_practice") or 0, -topics.index(row["topic"])))
        return _make_plan("review", oldest["topic"], class_level, practice, mastery, "practice_spaced_review_due", retention=retention)

    developing_topic = _latest_topic([t for t in mastery.get("developing_topics", []) if t in topics and t not in practice_mastered], mastery_rows)
    if developing_topic:
        return _make_plan("mastery_check", developing_topic, class_level, practice, mastery, "persistent_developing", retention=retention)

    practice_developing = [row for row in practice_rows.values() if row.get("mastery_status") == "developing" and row.get("topic") not in persistent_mastered]
    if practice_developing:
        weakest = min(practice_developing, key=lambda row: (row.get("mastery_estimate", 100), -row.get("evidence_questions", 0), topics.index(row["topic"])))
        return _make_plan("practice", weakest["topic"], class_level, practice, mastery, "practice_developing", retention=retention)

    target = _next_unmastered(class_level, mastered, practice.get("recommended_topic"))
    has_history = bool(practice.get("sessions") or mastery.get("topics"))
    return _make_plan("advance" if has_history else "practice", target, class_level, practice, mastery, "next_curriculum_topic" if has_history else "establish_baseline", retention=retention)


def build_autonomous_plan(learner_id, class_level):
    class_level = class_level if class_level in CLASS_TOPICS else "JSS2"
    practice = build_dashboard(learner_id, class_level)
    mastery = learner_summary(learner_id, class_level)
    mastery = _merge_intervention(mastery, learner_intervention_summary(learner_id, class_level))
    retention = learner_retention_summary(learner_id, class_level)
    return choose_next_action(class_level, practice, mastery, retention)
