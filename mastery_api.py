"""API for durable, pseudonymous learner mastery memory."""

import hashlib
import hmac
import os
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from classroom_api import _classroom_profiles, _enforce_rate_limit, _verify_session
from curriculum import CLASS_TOPICS
from learning_planner import build_autonomous_plan
from mastery_progress import infer_topic, learner_summary, persist_event, stage_event, teacher_summary
from misconceptions import classify_misconception, valid_intervention

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
    # Planner-selected interventions are allowlisted against the deterministic
    # misconception taxonomy before they can become durable evidence.
    intervention_category: str = Field(default="", max_length=80)
    intervention_strategy: str = Field(default="", max_length=700)


class MasterySummaryRequest(BaseModel):
    session_token: str = Field(min_length=20, max_length=300)
    class_level: Literal["JSS1", "JSS2", "JSS3"] = "JSS2"


class MasteryTeacherRequest(BaseModel):
    access_key: str = Field(min_length=16, max_length=200)
    class_level: Literal["JSS1", "JSS2", "JSS3"] = "JSS2"


def _verify_teacher(access_key: str) -> None:
    configured = os.getenv("TEACHER_DASHBOARD_KEY", "")
    if len(configured) < 16:
        raise HTTPException(status_code=503, detail="Teacher dashboard access is not configured")
    if not hmac.compare_digest(access_key, configured):
        raise HTTPException(status_code=403, detail="Incorrect teacher access key")


@router.post("/event")
def record_mastery_event(request: MasteryEventRequest, background_tasks: BackgroundTasks):
    student_id = _verify_session(request.session_token)
    _enforce_rate_limit(student_id, "mastery-memory", 40)
    profile = _classroom_profiles.get(student_id, {})
    class_level = profile.get("class_level", "JSS2")
    topic = infer_topic(request.lesson_text, class_level, request.topic_hint)
    if not topic or topic not in CLASS_TOPICS.get(class_level, ()):
        return {
            "stored": False,
            "reason": "topic_not_resolved",
            "summary": learner_summary(student_id, class_level),
        }

    diagnosis = None
    if not request.correct:
        diagnosis = classify_misconception(
            topic,
            request.question,
            request.selected_choice,
            request.correct_choice,
            request.feedback,
        )

    applied_category = request.intervention_category.strip()
    applied_strategy = request.intervention_strategy.strip()
    if not valid_intervention(applied_category, applied_strategy):
        applied_category = ""
        applied_strategy = ""

    event_id = hashlib.sha256(f"{student_id}:{request.check_id}:{request.stage}".encode()).hexdigest()[:32]
    record = stage_event(
        event_id,
        student_id,
        profile.get("learner_code", ""),
        class_level,
        topic,
        request.stage,
        request.correct,
        diagnosis["category"] if diagnosis else "",
        diagnosis["strategy"] if diagnosis else "",
        applied_category,
        applied_strategy,
    )
    background_tasks.add_task(persist_event, event_id)
    return {
        "stored": True,
        "topic": topic,
        "state": record["state"],
        "misconception": diagnosis if diagnosis else None,
        "strategy_outcome": record.get("strategy_outcome") or None,
        "summary": learner_summary(student_id, class_level),
    }


@router.post("/summary")
def get_mastery_summary(request: MasterySummaryRequest):
    student_id = _verify_session(request.session_token)
    _enforce_rate_limit(student_id, "mastery-summary", 30)
    profile = _classroom_profiles.get(student_id, {})
    class_level = profile.get("class_level", request.class_level)
    return learner_summary(student_id, class_level)


@router.post("/plan")
def get_autonomous_learning_plan(request: MasterySummaryRequest):
    student_id = _verify_session(request.session_token)
    _enforce_rate_limit(student_id, "autonomous-plan", 30)
    profile = _classroom_profiles.get(student_id, {})
    class_level = profile.get("class_level", request.class_level)
    return build_autonomous_plan(student_id, class_level)


@router.post("/teacher")
def get_teacher_mastery_summary(request: MasteryTeacherRequest):
    _verify_teacher(request.access_key)
    return teacher_summary(request.class_level)
