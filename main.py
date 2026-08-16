"""
Robo-Teacher -- WhatsApp + Telegram pilot bot (JSS2 Basic Maths).

Entry point: FastAPI app exposing webhooks for Twilio's WhatsApp Sandbox
and Telegram. New students are auto-registered on first contact via a
one-time "which school are you from?" question -- see roster_sheet.py.
See README.md for full setup and deployment steps.
"""

import datetime
import logging

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

load_dotenv()

from tutor import get_tutor_reply
from sheet_logger import log_interaction
from telegram_adapter import send_telegram_message
from roster_sheet import (
    lookup_student, is_awaiting_school_choice, mark_awaiting_school_choice,
    parse_school_choice, register_student, ONBOARDING_PROMPT, ONBOARDING_RETRY,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("robo-teacher")

app = FastAPI(title="Robo-Teacher Pilot")


@app.get("/")
def health_check():
    return {"status": "Robo-Teacher pilot bot is running"}


def _get_or_onboard(channel: str, identifier: str, message: str):
    """
    Checks whether this student is already registered.
    Returns either:
      ("reply", text)                              -- send this directly, no tutor call
      ("proceed", pilot_id, school, session_id)     -- go ahead and answer their question
    """
    student = lookup_student(channel, identifier)
    if student:
        pilot_id = student["pilot_id"]
        school = student["school"]
        session_id = f"{pilot_id}-{datetime.date.today().isoformat()}"
        return ("proceed", pilot_id, school, session_id)

    if is_awaiting_school_choice(channel, identifier):
        choice = parse_school_choice(message)
        if choice:
            school, prefix = choice
            pilot_id = register_student(channel, identifier, school, prefix)
            return ("reply", f"You're all set, {pilot_id}! \U0001F389 Ask me your first JSS2 Maths question anytime.")
        return ("reply", ONBOARDING_RETRY)

    mark_awaiting_school_choice(channel, identifier)
    return ("reply", ONBOARDING_PROMPT)


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    form = await request.form()
    from_number = form.get("From", "")  # e.g. "whatsapp:+2348012345678"
    body = (form.get("Body") or "").strip()

    twiml = MessagingResponse()

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
        reply_text, latency = get_tutor_reply(student_id=from_number, message=body)
    except Exception:
        logger.exception("Gemini call failed (WhatsApp)")
        reply_text, latency, status = "Sorry, I had a small technical hiccup. Please try asking again in a moment.", 0.0, "Error"

    # The reply is embedded directly in this same response, which Twilio
    # treats as a guaranteed direct reply to the message that just came in
    # (avoiding the separate outbound-message session-window check that a
    # follow-up API call would be subject to). Logging happens in the
    # background so it never delays the reply itself.
    twiml.message(reply_text)
    background_tasks.add_task(log_interaction, pilot_id, school, "WhatsApp", session_id, body, reply_text, latency, status)

    return Response(content=str(twiml), media_type="application/xml")


async def _handle_telegram_message(chat_id: int, text: str, pilot_id: str, school: str, session_id: str):
    """Runs after we've already told Telegram '200 OK', so a slow Gemini
    call can never cause Telegram to time out and retry the webhook."""
    status = "Success"
    try:
        reply_text, latency = get_tutor_reply(student_id=str(chat_id), message=text)
    except Exception:
        logger.exception("Gemini call failed (Telegram)")
        reply_text, latency, status = "Sorry, I had a small technical hiccup. Please try asking again in a moment.", 0.0, "Error"

    await send_telegram_message(chat_id, reply_text)
    log_interaction(pilot_id, school, "Telegram", session_id, text, reply_text, latency, status)


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    update = await request.json()
    message = update.get("message") or update.get("edited_message")

    if not message or "text" not in message:
        return {"ok": True}  # ignore non-text updates (stickers, photos, etc.)

    chat_id = message["chat"]["id"]
    username = (message.get("from") or {}).get("username", "")
    text = message["text"].strip()

    if not text:
        background_tasks.add_task(
            send_telegram_message, chat_id,
            "Hi! Send me a Maths question or topic you'd like help with (JSS2 syllabus)."
        )
        return {"ok": True}

    if not username:
        background_tasks.add_task(
            send_telegram_message, chat_id,
            "You'll need a Telegram username set (Settings \u2192 Username) before I can register you \u2014 "
            "add one, then message me again!"
        )
        return {"ok": True}

    outcome = _get_or_onboard("telegram", username, text)

    if outcome[0] == "reply":
        background_tasks.add_task(send_telegram_message, chat_id, outcome[1])
        return {"ok": True}

    _, pilot_id, school, session_id = outcome
    background_tasks.add_task(_handle_telegram_message, chat_id, text, pilot_id, school, session_id)
    return {"ok": True}
