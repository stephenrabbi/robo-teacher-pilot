"""Robo-Teacher — WhatsApp + Telegram pilot bot (JSS2 Basic Maths)."""
import datetime
import logging
import os
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import Response
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
load_dotenv()
from tutor import get_tutor_reply, get_tutor_image_reply, get_tutor_audio_reply
from sheet_logger import log_interaction
from telegram_adapter import send_telegram_message, configure_telegram_webhook, download_telegram_image, download_telegram_audio, SUPPORTED_AUDIO_MIME_TYPES
from roster_sheet import lookup_student, is_awaiting_school_choice, mark_awaiting_school_choice, parse_school_choice, register_student, auto_enrollment_enabled, ONBOARDING_PROMPT, ONBOARDING_RETRY, ENROLLMENT_CLOSED_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("robo-teacher")
app = FastAPI(title="Robo-Teacher Pilot")
WHATSAPP_MIGRATION_MESSAGE = "Robo-Teacher WhatsApp Pilot Update\n\nOur WhatsApp pilot has now ended while we improve Robo-Teacher.\n\nPlease continue learning with Robo-Teacher FREE on Telegram:\nhttps://t.me/RoboTeacherAfricaBot\n\nOpen the link, tap Start, and continue asking your Maths questions there.\n\nThank you for being part of the Robo-Teacher journey.\nEvery learner. Their own AI teacher."

@app.on_event("startup")
async def _sync_telegram_webhook_on_startup():
    try:
        await configure_telegram_webhook()
        logger.info("Telegram webhook synchronized successfully")
    except Exception: logger.exception("Telegram webhook synchronization failed")

def whatsapp_migration_mode_enabled(): return os.getenv("WHATSAPP_MIGRATION_MODE", "true").strip().lower() in {"1","true","yes","on"}
def _validate_twilio_request(request, form):
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    if not auth_token: raise HTTPException(status_code=500, detail="Twilio authentication is not configured")
    if not RequestValidator(auth_token).validate(str(request.url), dict(form), request.headers.get("X-Twilio-Signature", "")): raise HTTPException(status_code=403, detail="Invalid Twilio signature")
def _validate_telegram_request(request):
    secret = os.getenv("TELEGRAM_WEBHOOK_SECRET")
    if not secret: raise HTTPException(status_code=500, detail="Telegram webhook authentication is not configured")
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token", "") != secret: raise HTTPException(status_code=403, detail="Invalid Telegram webhook secret")

@app.get("/")
def health_check(): return {"status":"Robo-Teacher pilot bot is running"}

def _get_or_onboard(channel, identifier, message):
    student = lookup_student(channel, identifier)
    if student:
        pilot_id, school = student["pilot_id"], student["school"]
        return "proceed", pilot_id, school, f"{pilot_id}-{datetime.date.today().isoformat()}"
    if not auto_enrollment_enabled(): return "reply", ENROLLMENT_CLOSED_PROMPT
    if is_awaiting_school_choice(channel, identifier):
        choice = parse_school_choice(message)
        if choice:
            school, prefix = choice
            pilot_id = register_student(channel, identifier, school, prefix)
            return "reply", f"You're all set, {pilot_id}! 🎉 Ask me your first JSS2 Maths question anytime."
        return "reply", ONBOARDING_RETRY
    mark_awaiting_school_choice(channel, identifier)
    return "reply", ONBOARDING_PROMPT

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    form = await request.form(); _validate_twilio_request(request, form); twiml = MessagingResponse()
    if whatsapp_migration_mode_enabled(): twiml.message(WHATSAPP_MIGRATION_MESSAGE); return Response(content=str(twiml), media_type="application/xml")
    from_number, body = form.get("From", ""), (form.get("Body") or "").strip()
    if not body: twiml.message("Hi! Send me a Maths question or topic you'd like help with (JSS2 syllabus)."); return Response(content=str(twiml), media_type="application/xml")
    outcome = _get_or_onboard("whatsapp", from_number, body)
    if outcome[0] == "reply": twiml.message(outcome[1]); return Response(content=str(twiml), media_type="application/xml")
    _, pilot_id, school, session_id = outcome; status = "Success"
    try: reply_text, latency = get_tutor_reply(pilot_id, body)
    except Exception: logger.exception("Gemini call failed (WhatsApp)"); reply_text, latency, status = "Sorry, I had a small technical hiccup. Please try asking again in a moment.", 0.0, "Error"
    twiml.message(reply_text); background_tasks.add_task(log_interaction, pilot_id, school, "WhatsApp", session_id, body, reply_text, latency, status)
    return Response(content=str(twiml), media_type="application/xml")

async def _handle_telegram_message(chat_id, text, pilot_id, school, session_id):
    status="Success"
    try: reply_text, latency = get_tutor_reply(pilot_id, text)
    except Exception: logger.exception("Gemini call failed (Telegram)"); reply_text, latency, status = "Sorry, I had a small technical hiccup. Please try asking again in a moment.",0.0,"Error"
    await send_telegram_message(chat_id, reply_text); log_interaction(pilot_id, school, "Telegram", session_id, text, reply_text, latency, status)

async def _handle_telegram_image(chat_id, file_id, caption, pilot_id, school, session_id):
    status="Success"
    try:
        media, mime = await download_telegram_image(file_id); reply_text, latency = get_tutor_image_reply(pilot_id, media, mime, caption)
    except ValueError as exc: reply_text, latency, status = f"I couldn't use that image safely: {exc}. Please send a clear JPG, PNG, or WEBP photo of the Maths question.",0.0,"RejectedImage"
    except Exception: logger.exception("Image tutoring failed (Telegram)"); reply_text, latency, status = "Sorry, I couldn't read that image just now. Please try again with a clear photo or type the Maths question.",0.0,"Error"
    await send_telegram_message(chat_id, reply_text); log_interaction(pilot_id, school, "Telegram", session_id, "[Maths image received]" + (f" Caption: {caption[:180]}" if caption else ""), reply_text, latency, status)

async def _handle_telegram_audio(chat_id, file_id, mime_type, pilot_id, school, session_id):
    """Understand a voice note transiently; never store the recording or transcript."""
    status="Success"
    try:
        audio, resolved_mime = await download_telegram_audio(file_id, mime_type); reply_text, latency = get_tutor_audio_reply(pilot_id, audio, resolved_mime)
    except ValueError as exc: reply_text, latency, status = f"I couldn't use that voice note safely: {exc}. Please send a shorter clear voice note or type your Maths question.",0.0,"RejectedAudio"
    except Exception: logger.exception("Voice tutoring failed (Telegram)"); reply_text, latency, status = "Sorry, I couldn't understand that voice note just now. Please try again or type the Maths question.",0.0,"Error"
    await send_telegram_message(chat_id, reply_text); log_interaction(pilot_id, school, "Telegram", session_id, "[Maths voice note received]", reply_text, latency, status)

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    _validate_telegram_request(request); update = await request.json(); message = update.get("message") or update.get("edited_message")
    if not message: return {"ok":True}
    chat_id = message["chat"]["id"]; username = (message.get("from") or {}).get("username", ""); text = (message.get("text") or message.get("caption") or "").strip()
    photos = message.get("photo") or []; document = message.get("document") or {}; document_mime = str(document.get("mime_type", ""))
    image_file_id = photos[-1]["file_id"] if photos else (document.get("file_id") if document_mime in {"image/jpeg","image/png","image/webp"} else None)
    voice = message.get("voice") or {}; audio = message.get("audio") or {}; audio_obj = voice or audio
    audio_mime = str(audio_obj.get("mime_type", "")); audio_file_id = audio_obj.get("file_id") if audio_obj and (not audio_mime or audio_mime in SUPPORTED_AUDIO_MIME_TYPES) else None
    if not username: background_tasks.add_task(send_telegram_message, chat_id, "You'll need a Telegram username set (Settings → Username) before I can register you — add one, then message me again!"); return {"ok":True}
    onboarding_text = text or ("Maths image" if image_file_id else "") or ("Maths voice note" if audio_file_id else "")
    if not onboarding_text: background_tasks.add_task(send_telegram_message, chat_id, "Send a JSS2 Maths question by text, a clear homework photo, or a short voice note."); return {"ok":True}
    outcome = _get_or_onboard("telegram", username, onboarding_text)
    if outcome[0] == "reply": background_tasks.add_task(send_telegram_message, chat_id, outcome[1]); return {"ok":True}
    _, pilot_id, school, session_id = outcome
    if image_file_id: background_tasks.add_task(_handle_telegram_image, chat_id, image_file_id, text, pilot_id, school, session_id)
    elif audio_file_id: background_tasks.add_task(_handle_telegram_audio, chat_id, audio_file_id, audio_mime, pilot_id, school, session_id)
    else: background_tasks.add_task(_handle_telegram_message, chat_id, text, pilot_id, school, session_id)
    return {"ok":True}
