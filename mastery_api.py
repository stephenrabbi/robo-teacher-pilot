"""API for durable, pseudonymous learner mastery memory."""

import hashlib
import hmac
import os
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from autopilot_progress import persist_session_event, session_status, start_or_resume_session, transition_session
from classroom_api import _classroom_profiles, _enforce_rate_limit, _verify_session
from curriculum import CLASS_TOPICS
from intervention_support import learner_intervention_summary, teacher_intervention_summary
from learning_planner import build_autonomous_plan
from mastery_progress import infer_topic, learner_summary, persist_event, stage_event, teacher_summary
from misconceptions import classify_misconception
from retention_progress import (
    is_review_due,
    learner_retention_summary,
    persist_event as persist_retention_event,
    record_review_result,
    schedule_after_mastery,
)

router = APIRouter(prefix="/api/classroom/mastery", tags=["classroom-mastery"])


class MasteryEventRequest(BaseModel):
    session_token: str = Field(min_length=20, max_length=300)
    lesson_text: str = Field(default="", max_length=6000)
    topic_hint: str = Field(default="", max_length=80)
    check_id: str = Field(min_length=16, max_length=64, pattern=r"^[a-f0-9]+$")
    stage: Literal["initial", "reteach"] = "initial"
    correct: bool
    # These fields are used only for deterministic classification. They are
    # deliberately not written to durable storage.
    question: str = Field(default="", max_length=1000)
    selected_choice: str = Field(default="", max_length=500)
    correct_choice: str = Field(default="", max_length=500)
    feedback: str = Field(default="", max_length=1500)


class MasterySummaryRequest(BaseModel):
    session_token: str = Field(min_length=20, max_length=300)
    class_level: Literal["JSS1", "JSS2", "JSS3"] = "JSS2"


class MasteryTeacherRequest(BaseModel):
    access_key: str = Field(min_length=16, max_length=200)
    class_level: Literal["JSS1", "JSS2", "JSS3"] = "JSS2"


class AutopilotSessionRequest(BaseModel):
    session_token: str = Field(min_length=20, max_length=300)
    class_level: Literal["JSS1", "JSS2", "JSS3"] = "JSS2"
    action: Literal["status", "start", "step", "pause", "resume", "stop", "finish"] = "status"
    session_id: str = Field(default="", max_length=64, pattern=r"^[a-f0-9]*$")
    completed_steps: int = Field(default=0, ge=0, le=3)


def _verify_teacher(access_key: str) -> None:
    configured = os.getenv("TEACHER_DASHBOARD_KEY", "")
    if len(configured) < 16:
        raise HTTPException(status_code=503, detail="Teacher dashboard access is not configured")
    if not hmac.compare_digest(access_key, configured):
        raise HTTPException(status_code=403, detail="Incorrect teacher access key")


def _learner_summary(student_id: str, class_level: str) -> dict:
    summary = learner_summary(student_id, class_level)
    intervention = learner_intervention_summary(student_id, class_level)
    retention = learner_retention_summary(student_id, class_level)
    summary.update({
        "teacher_support_required": intervention["teacher_support_required"],
        "teacher_support_topics": intervention["teacher_support_topics"],
        "watch_topics": intervention["watch_topics"],
        "interventions": intervention["interventions"],
        "teacher_support_focus": intervention["teacher_support_focus"],
        "retention": retention,
        "retention_due_topics": retention["due_topics"],
        "retention_lapse_topics": retention["retention_lapse_topics"],
        "storage_synced": (
            bool(summary.get("storage_synced"))
            and bool(intervention.get("storage_synced"))
            and bool(retention.get("storage_synced"))
        ),
    })
    return summary


def _teacher_summary(class_level: str) -> dict:
    summary = teacher_summary(class_level)
    intervention = teacher_intervention_summary(class_level)
    summary.update({
        "teacher_support_count": intervention["teacher_support_count"],
        "teacher_support_learners": intervention["teacher_support_learners"],
        "intervention_learners": intervention["intervention_learners"],
        "storage_synced": bool(summary.get("storage_synced")) and bool(intervention.get("storage_synced")),
    })
    return summary


@router.post("/event")
def record_mastery_event(request: MasteryEventRequest, background_tasks: BackgroundTasks):
    student_id = _verify_session(request.session_token)
    _enforce_rate_limit(student_id, "mastery-memory", 40)
    profile = _classroom_profiles.get(student_id, {})
    learner_code = profile.get("learner_code", "")
    class_level = profile.get("class_level", "JSS2")
    topic = infer_topic(request.lesson_text, class_level, request.topic_hint)
    if not topic or topic not in CLASS_TOPICS.get(class_level, ()):
        return {
            "stored": False,
            "reason": "topic_not_resolved",
            "summary": _learner_summary(student_id, class_level),
        }

    retention_review = request.stage == "initial" and is_review_due(student_id, class_level, topic)
    diagnosis = None
    if not request.correct:
        diagnosis = classify_misconception(
            topic,
            request.question,
            request.selected_choice,
            request.correct_choice,
            request.feedback,
        )

    event_id = hashlib.sha256(f"{student_id}:{request.check_id}:{request.stage}".encode()).hexdigest()[:32]
    record = stage_event(
        event_id,
        student_id,
        learner_code,
        class_level,
        topic,
        request.stage,
        request.correct,
        diagnosis["category"] if diagnosis else "",
        diagnosis["strategy"] if diagnosis else "",
    )
    background_tasks.add_task(persist_event, event_id)

    retention_record = None
    if retention_review:
        retention_record = record_review_result(
            event_id,
            student_id,
            learner_code,
            class_level,
            topic,
            request.correct,
        )
        background_tasks.add_task(persist_retention_event, retention_record["event_id"])

        # A successful scheduled retrieval check is itself strong mastery
        # evidence. Promote it server-side so review does not accidentally
        # downgrade a previously mastered topic to merely "developing".
        if request.correct:
            confirmation_id = hashlib.sha256(f"{event_id}:retention-confirmed".encode()).hexdigest()[:32]
            record = stage_event(
                confirmation_id,
                student_id,
                learner_code,
                class_level,
                topic,
                "reteach",
                True,
            )
            background_tasks.add_task(persist_event, confirmation_id)
    elif record.get("state") == "mastered":
        retention_record = schedule_after_mastery(
            event_id,
            student_id,
            learner_code,
            class_level,
            topic,
        )
        background_tasks.add_task(persist_retention_event, retention_record["event_id"])

    return {
        "stored": True,
        "topic": topic,
        "state": record["state"],
        "misconception": diagnosis if diagnosis else None,
        "retention_review": bool(retention_review),
        "retention_outcome": retention_record.get("outcome") if retention_record else None,
        "next_review_at": retention_record.get("next_review_at") if retention_record else None,
        "retention_interval_days": retention_record.get("interval_days") if retention_record else None,
        "summary": _learner_summary(student_id, class_level),
    }


@router.post("/summary")
def get_mastery_summary(request: MasterySummaryRequest):
    student_id = _verify_session(request.session_token)
    _enforce_rate_limit(student_id, "mastery-summary", 30)
    profile = _classroom_profiles.get(student_id, {})
    class_level = profile.get("class_level", request.class_level)
    return _learner_summary(student_id, class_level)


@router.post("/plan")
def get_autonomous_learning_plan(request: MasterySummaryRequest):
    student_id = _verify_session(request.session_token)
    _enforce_rate_limit(student_id, "autonomous-plan", 30)
    profile = _classroom_profiles.get(student_id, {})
    class_level = profile.get("class_level", request.class_level)
    return build_autonomous_plan(student_id, class_level)


@router.post("/autopilot/session")
def manage_autopilot_session(request: AutopilotSessionRequest, background_tasks: BackgroundTasks):
    """Start, resume and checkpoint bounded Autopilot sessions without storing lesson content."""
    student_id = _verify_session(request.session_token)
    _enforce_rate_limit(student_id, "autopilot-session", 60)
    profile = _classroom_profiles.get(student_id, {})
    class_level = profile.get("class_level", request.class_level)

    if request.action == "status":
        return session_status(student_id, class_level)

    if request.action == "start":
        result = start_or_resume_session(student_id, class_level)
    else:
        if not request.session_id:
            raise HTTPException(status_code=400, detail="Autopilot session ID is required")
        status = {
            "step": "active",
            "pause": "paused",
            "resume": "active",
            "stop": "stopped",
            "finish": "complete",
        }[request.action]
        try:
            result = transition_session(
                student_id,
                class_level,
                request.session_id,
                status,
                request.completed_steps,
            )
        except ValueError as exc:
            if str(exc) == "session_not_found":
                raise HTTPException(status_code=404, detail="Autopilot session was not found") from exc
            raise HTTPException(status_code=400, detail="Invalid Autopilot session state") from exc

    event_id = result.pop("event_id", None)
    if event_id:
        background_tasks.add_task(persist_session_event, event_id)
    return result


@router.post("/teacher")
def get_teacher_mastery_summary(request: MasteryTeacherRequest):
    _verify_teacher(request.access_key)
    return _teacher_summary(request.class_level)
