"""Subject teaching routes share signed sessions but not Maths progress/history."""
from typing import Literal
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field, ConfigDict
from starlette.concurrency import run_in_threadpool
import classroom_api
import subject_tutor

router=APIRouter(prefix="/api/classroom/subject",tags=["subject teaching"])
Subject=Literal["English Language","Basic Science"]
Language=Literal["English","Yoruba","Igbo","Hausa"]

class SubjectQuestion(BaseModel):
    model_config=ConfigDict(extra="forbid")
    message: str=Field(min_length=1,max_length=1200)
    session_token: str=Field(min_length=20,max_length=300)
    subject: Subject
    language: Language="English"
    conversation_id: str=Field(pattern=r"^[a-f0-9]{32}$")

def _identity(token):
    student_id=classroom_api._verify_session(token)
    classroom_api._enforce_rate_limit(student_id)
    return student_id,classroom_api._classroom_profiles.get(student_id,{}).get("class_level","JSS2")

def _teach(student_id,class_level,subject,language,conversation_id,message,media_bytes=None,mime_type=None):
    if not message.strip() and media_bytes is None:
        raise HTTPException(status_code=422,detail="Please enter a question")
    try:
        reply,latency=subject_tutor.teach(student_id,subject,language,class_level,conversation_id,message,media_bytes,mime_type)
    except Exception:
        raise HTTPException(status_code=503,detail="The subject teacher is temporarily unavailable. Your question is still available to retry.")
    return {"reply":reply,"latency_seconds":round(latency,3),"subject":subject}

@router.post("/chat")
def chat(request:SubjectQuestion):
    student_id,class_level=_identity(request.session_token)
    return _teach(student_id,class_level,request.subject,request.language,request.conversation_id,request.message)

@router.post("/{kind}")
async def media(kind:Literal["image","audio"],session_token:str=Form(...,min_length=20,max_length=300),subject:Subject=Form(...),conversation_id:str=Form(...,pattern=r"^[a-f0-9]{32}$"),language:Language=Form("English"),caption:str=Form("",max_length=500),file:UploadFile=File(...)):
    student_id,class_level=_identity(session_token)
    mime=(file.content_type or "").split(";",1)[0].lower()
    supported=classroom_api.SUPPORTED_IMAGE_MIME_TYPES if kind=="image" else classroom_api.SUPPORTED_AUDIO_MIME_TYPES
    if mime not in supported:
        raise HTTPException(status_code=415,detail="Unsupported educational media type")
    limit=8*1024*1024 if kind=="image" else 12*1024*1024
    content=await file.read(limit+1)
    if not content or len(content)>limit:
        raise HTTPException(status_code=422,detail="The file is empty or too large")
    prompt=caption or ("Explain the educational question in this image." if kind=="image" else "Listen carefully to the learner's question and teach the answer. Ask for clarification if anything essential is unclear.")
    return await run_in_threadpool(_teach,student_id,class_level,subject,language,conversation_id,prompt,content,mime)
