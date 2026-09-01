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

from tutor import get_tutor_reply
from sheet_logger import log_interaction
from telegram_adapter import send_telegram_message
from roster_sheet import (
    lookup_student, is_awaiting_school_choice, mark_awaiting_school_choice,
    parse_school_choice, register_student, auto_enrollment_enabled,
    ONBOARDING_PROMPT, ONBOARDING_RETRY, ENROLLMENT_CLOSED_PROMPT,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("robo-teacher")
app = FastAPI(title="Robo-Teacher Pilot")

WHATSAPP_MIGRATION_MESSAGE = (
    "Robo-Teacher WhatsApp Pilot Update\n\n"
    "Our WhatsApp pilot has now ended while we improve Robo-Teacher.\n\n"
    "Please continue learning with Robo-Teacher FREE on Telegram:\n"
    "https://t.me/RoboTeacherAfricaBot\n\n"
    "Open the link, tap Start, and continue asking your Maths questions there.\n\n"
    "Thank you for being part of the Robo-Teacher journey.\n"
    "Every learner. Their own AI teacher."
)


def whatsapp_migration_mode_enabled() -> bool:
    """Keep WhatsApp in migration-only mode unless explicitly disabled."""
    return os.getenv("WHATSAPP_MIGRATION_MODE", "true").strip().lower() in {
        "1", "true", "yes", "on"
    }


def _validate_twilio_request(request: Request, form) -> None:
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    if not auth_token:
        raise HTTPException(status_code=500, detail="Twilio authentication is not configured")
    signature = request.headers.get("X-Twilio-Signature", "")
    validator = RequestValidator(auth_token)
    if not validator.validate(str(request.url), dict(form), signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")


def _validate_telegram_request(request: Request) -> None:
    secret = os.getenv("TELEGRAM_WEBHOOK_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="Telegram webhook authentication is not configured")
    supplied = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if supplied != secret:
        raise HTTPException(status_code=403, detail="Invalid Telegram webhook secret")


@app.get("/")
def health_check():
    return {"status": "Robo-Teacher pilot bot is running"}


def _get_or_onboard(channel: str, identifier: str, message: str):
    student = lookup_student(channel, identifier)
    if student:
        pilot_id = student["pilot_id"]
        school = student["school"]
        session_id = f"{pilot_id}-{datetime.date.today().isoformat()}"
        return ("proceed", pilot_id, school, session_id)

    # The production pilot is closed by default. Existing roster entries above
    # continue to work; unknown identifiers cannot self-register.
    if not auto_enrollment_enabled():
        return ("reply", ENROLLMENT_CLOSED_PROMPT)

    if is_awaiting_school_choice(channel, identifier):
        choice = parse_school_choice(message)
        if choice:
            school, prefix = choice
            pilot_id = register_student(channel, identifier, school, prefix)
            return ("reply", f"You're all set, {pilot_id}! 🎉 Ask me your first JSS2 Maths question anytime.")
        return ("reply", ONBOARDING_RETRY)

    mark_awaiting_school_choice(channel, identifier)
    return ("reply", ONBOARDING_PROMPT)


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    form = await request.form()
    _validate_twilio_request(request, form)
    twiml = MessagingResponse()

    # Temporary migration mode: WhatsApp no longer calls Gemini, performs
    # onboarding, or logs a tutoring interaction. It only directs users to
    # the active Telegram bot. This keeps the Telegram learning service live
    # while the completed WhatsApp pilot is being wound down.
    if whatsapp_migration_mode_enabled():
        twiml.message(WHATSAPP_MIGRATION_MESSAGE)
        return Response(content=str(twiml), media_type="application/xml")

    from_number = form.get("From", "")
    body = (form.get("Body") or "").strip()

    if not body:
        twiml.message("Hi! Send me a Maths question or topic you'd like help with (JSS2 syllabus).")
        return Response(content=str(twiml), media_type="application/xml")

    outcome = _get_or_onboard("whatsapp", from_number, body)
    if outcome[0] == "reply":
        twiml.message(outcome[1])
        return Response(content=str(twiml), media_type="application/xml")

    _, pilot_id, school, session_id = outcome
    status = "Success"
    try:
        reply_text, latency = get_tutor_reply(student_id=pilot_id, message=body)
    except Exception:
        logger.exception("Gemini call failed (WhatsApp)")
        reply_text, latency, status = "Sorry, I had a small technical hiccup. Please try asking again in a moment.", 0.0, "Error"
    twiml.message(reply_text)
    background_tasks.add_task(log_interaction, pilot_id, school, "WhatsApp", session_id, body, reply_text, latency, status)
    return Response(content=str(twiml), media_type="application/xml")


async def _handle_telegram_message(chat_id: int, text: str, pilot_id: str, school: str, session_id: str):
    status = "Success"
    try:
        reply_text, latency = get_tutor_reply(student_id=pilot_id, message=text)
    except Exception:
        logger.exception("Gemini call failed (Telegram)")
        reply_text, latency, status = "Sorry, I had a small technical hiccup. Please try asking again in a moment.", 0.0, "Error"
    await send_telegram_message(chat_id, reply_text)
    log_interaction(pilot_id, school, "Telegram", session_id, text, reply_text, latency, status)


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    _validate_telegram_request(request)
    update = await request.json()
    message = update.get("message") or update.get("edited_message")
    if not message or "text" not in message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    username = (message.get("from") or {}).get("username", "")
    text = message["text"].strip()

    if not text:
        background_tasks.add_task(send_telegram_message, chat_id, "Hi! Send me a Maths question or topic you'd like help with (JSS2 syllabus).")
        return {"ok": True}

    if not username:
        background_tasks.add_task(send_telegram_message, chat_id, "You'll need a Telegram username set (Settings → Username) before I can register you — add one, then message me again!")
        return {"ok": True}

    outcome = _get_or_onboard("telegram", username, text)
    if outcome[0] == "reply":
        background_tasks.add_task(send_telegram_message, chat_id, outcome[1])
        return {"ok": True}

    _, pilot_id, school, session_id = outcome
    background_tasks.add_task(_handle_telegram_message, chat_id, text, pilot_id, school, session_id)
    return {"ok": True}
