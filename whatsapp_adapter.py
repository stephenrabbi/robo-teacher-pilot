"""
Sends WhatsApp replies via Twilio's REST API, rather than embedding the
reply directly in the synchronous TwiML webhook response.

Why: Twilio's webhook has a short timeout (~15s). If a cold-started
Render instance plus a Gemini call together take longer than that, the
synchronous TwiML approach fails silently, and the student sees nothing.
This adapter lets us acknowledge Twilio's webhook instantly, then send
the real answer whenever it's actually ready.
"""

import os
from twilio.rest import Client

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
    return _client


def send_whatsapp_message(to_whatsapp_number: str, body: str) -> None:
    """to_whatsapp_number should already include the 'whatsapp:' prefix, e.g. 'whatsapp:+2348012345678'."""
    client = _get_client()
    sandbox_number = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
    client.messages.create(from_=sandbox_number, to=to_whatsapp_number, body=body)
