"""
Robo-Teacher — WhatsApp pilot bot (JSS2 Basic Maths).

Entry point: FastAPI app exposing a single webhook for Twilio's
WhatsApp Sandbox. See README.md for full setup and deployment steps.
"""

import os
import json
import logging

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

load_dotenv()

from tutor import get_tutor_reply
from sheet_logger import log_interaction
from telegram_adapter import send_telegram_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("robo-teacher")

app = FastAPI(title="Robo-Teacher Pilot")

_ROSTER_PATH = os.path.join(os.path.dirname(__file__), "roster.json")
try:
    with open(_ROSTER_PATH) as f:
        _raw_roster = json.load(f)
        _ROSTER = {
            "whatsapp": _raw_roster.get("whatsapp", {}),
            "telegram": _raw_roster.get("telegram", {}),
        }
except FileNotFoundError:
    _ROSTER = {"whatsapp": {}, "telegram": {}}


def _lookup_school(identifier: str, platform: str) -> str:
    digits = "".join(c for c in identifier if c.isdigit())
    return _ROSTER[platform].get(digits, "Unregistered")


@app.get("/")
def health_check():
    return {"status": "Robo-Teacher pilot bot is running"}


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    form = await request.form()
    from_number = form.get("From", "")  # e.g. "whatsapp:+2348012345678"
    body = (form.get("Body") or "").strip()

    twiml = MessagingResponse()

    if not body:
        twiml.message("Hi! Send me a Maths question or topic you'd like help with (JSS2 syllabus).")
        return Response(content=str(twiml), media_type="application/xml")

    school = _lookup_school(from_number, "whatsapp")

    try:
        reply_text, latency = get_tutor_reply(student_id=from_number, message=body)
    except Exception as e:
        logger.exception("Gemini call failed")
        twiml.message("Sorry, I had a small technical hiccup. Please try asking again in a moment.")
        return Response(content=str(twiml), media_type="application/xml")

    twiml.message(reply_text)

    # Log in the background so it never slows down the reply to the student.
    background_tasks.add_task(log_interaction, from_number, school, body, reply_text, latency)

    return Response(content=str(twiml), media_type="application/xml")


async def _handle_telegram_message(chat_id: int, text: str, school: str):
    """Runs after we've already told Telegram '200 OK', so a slow Gemini
    call can never cause Telegram to time out and retry the webhook."""
    try:
        reply_text, latency = get_tutor_reply(student_id=str(chat_id), message=text)
    except Exception:
        logger.exception("Gemini call failed (Telegram)")
        reply_text, latency = "Sorry, I had a small technical hiccup. Please try asking again in a moment.", 0.0

    await send_telegram_message(chat_id, reply_text)
    log_interaction(str(chat_id), school, text, reply_text, latency)


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    update = await request.json()
    message = update.get("message") or update.get("edited_message")

    if not message or "text" not in message:
        return {"ok": True}  # ignore non-text updates (stickers, photos, etc.)

    chat_id = message["chat"]["id"]
    text = message["text"].strip()
    school = _lookup_school(str(chat_id), "telegram")

    if not text:
        background_tasks.add_task(
            send_telegram_message, chat_id,
            "Hi! Send me a Maths question or topic you'd like help with (JSS2 syllabus)."
        )
        return {"ok": True}

    background_tasks.add_task(_handle_telegram_message, chat_id, text, school)
    return {"ok": True}
