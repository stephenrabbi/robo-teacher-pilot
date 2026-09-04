"""Browser API for the Robo-Teacher V2.5 classroom.

The browser receives a short-lived signed pseudonymous session. No Gemini key or
provider credential is ever exposed to JavaScript. The server reuses the same
Robo-Teacher tutoring engine used by the messaging channels.
"""
import hashlib
import hmac
import os
import secrets
import time
from collections import defaultdict, deque

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field

from tutor import (
    MAX_AUDIO_BYTES,
    MAX_IMAGE_BYTES,
    SUPPORTED_AUDIO_MIME_TYPES,
    SUPPORTED_IMAGE_MIME_TYPES,
    get_tutor_audio_reply,
    get_tutor_image_reply,
    get_tutor_reply,
)

router = APIRouter(prefix="/api/classroom", tags=["classroom"])
_SESSION_TTL_SECONDS = 60 * 60 * 4
_RATE_WINDOW_SECONDS = 60
_RATE_MAX_REQUESTS = 12
_SESSION_KEY = os.getenv("CLASSROOM_SESSION_SECRET", "").encode() or secrets.token_bytes(32)
_request_times: dict[str, deque] = defaultdict(deque)


class ClassroomQuestion(BaseModel):
    message: str = Field(min_length=1, max_length=1200)
    session_token: str = Field(min_length=20, max_length=300)


def _sign(payload: str) -> str:
    return hmac.new(_SESSION_KEY, payload.encode(), hashlib.sha256).hexdigest()


def _new_session() -> tuple[str, str]:
    student_id = f"WEB-{secrets.token_hex(8)}"
    issued = str(int(time.time()))
    payload = f"{student_id}.{issued}"
    return student_id, f"{payload}.{_sign(payload)}"


def _verify_session(token: str) -> str:
    try:
        student_id, issued, signature = token.split(".", 2)
        issued_int = int(issued)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid classroom session")
    payload = f"{student_id}.{issued}"
    if not hmac.compare_digest(signature, _sign(payload)):
        raise HTTPException(status_code=401, detail="Invalid classroom session")
    now = int(time.time())
    if issued_int > now + 60 or now - issued_int > _SESSION_TTL_SECONDS:
        raise HTTPException(status_code=401, detail="Classroom session expired")
    if not student_id.startswith("WEB-"):
        raise HTTPException(status_code=401, detail="Invalid classroom session")
    return student_id


def _enforce_rate_limit(student_id: str) -> None:
    now = time.time()
    bucket = _request_times[student_id]
    while bucket and now - bucket[0] > _RATE_WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= _RATE_MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Please wait a moment before asking another question")
    bucket.append(now)


@router.post("/session")
def create_classroom_session():
    student_id, token = _new_session()
    return {"session_token": token, "learner_id": student_id, "expires_in": _SESSION_TTL_SECONDS}


@router.post("/chat")
def classroom_chat(question: ClassroomQuestion, request: Request):
    student_id = _verify_session(question.session_token)
    _enforce_rate_limit(student_id)
    message = question.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Question cannot be empty")
    try:
        reply, latency = get_tutor_reply(student_id, message)
    except Exception as exc:
        # Never expose provider details, prompts, credentials, or stack traces to learners.
        raise HTTPException(status_code=503, detail="Robo-Teacher is temporarily unavailable") from exc
    return {"reply": reply, "latency_seconds": round(float(latency), 3), "learner_id": student_id}


@router.post("/image")
async def classroom_image(
    session_token: str = Form(..., min_length=20, max_length=300),
    image: UploadFile = File(...),
    caption: str = Form("", max_length=500),
):
    student_id = _verify_session(session_token)
    _enforce_rate_limit(student_id)
    mime_type = (image.content_type or "").lower()
    if mime_type not in SUPPORTED_IMAGE_MIME_TYPES:
        raise HTTPException(status_code=415, detail="Please upload a JPEG, PNG, or WebP image")
    image_bytes = await image.read(MAX_IMAGE_BYTES + 1)
    if not image_bytes:
        raise HTTPException(status_code=422, detail="The image is empty")
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="The image must be 8 MB or smaller")
    try:
        reply, latency = get_tutor_image_reply(student_id, image_bytes, mime_type, caption.strip())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="The image could not be processed") from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Robo-Teacher is temporarily unavailable") from exc
    return {"reply": reply, "latency_seconds": round(float(latency), 3), "learner_id": student_id}


@router.post("/audio")
async def classroom_audio(
    session_token: str = Form(..., min_length=20, max_length=300),
    audio: UploadFile = File(...),
):
    student_id = _verify_session(session_token)
    _enforce_rate_limit(student_id)
    mime_type = (audio.content_type or "").split(";", 1)[0].lower()
    if mime_type not in SUPPORTED_AUDIO_MIME_TYPES:
        raise HTTPException(status_code=415, detail="Please record or upload a supported audio file")
    audio_bytes = await audio.read(MAX_AUDIO_BYTES + 1)
    if not audio_bytes:
        raise HTTPException(status_code=422, detail="The recording is empty")
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="The recording must be 12 MB or smaller")
    try:
        reply, latency = get_tutor_audio_reply(student_id, audio_bytes, mime_type)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="The recording could not be processed") from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Robo-Teacher is temporarily unavailable") from exc
    return {"reply": reply, "latency_seconds": round(float(latency), 3), "learner_id": student_id}
