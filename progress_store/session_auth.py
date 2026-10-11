"""Isolated signed-session verification prototype; NOT a production login flow.

Tokens are issued only by trusted server code after identity verification.
The public classroom must never be allowed to request arbitrary subject tokens.
"""
from dataclasses import dataclass
import base64
import hashlib
import hmac
import json
import time

from .prototype import Principal

AUDIENCE = "robo-teacher-progress-v1"
MAX_AGE_SECONDS = 3600

def _b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

def _unb64(value):
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))

def _validate_secret(secret):
    if not isinstance(secret, bytes) or len(secret) < 32:
        raise ValueError("A server-held secret of at least 32 bytes is required")

def issue_test_session(*, subject, school, secret, now=None, ttl=900, session_epoch=None):
    """Only for synthetic identity tests. Not wired to API routes."""
    _validate_secret(secret)
    if not isinstance(subject, str) or not isinstance(school, str) or not subject.strip() or not school.strip():
        raise ValueError("A verified nonempty subject and school are required")
    if type(ttl) is not int or not 1 <= ttl <= MAX_AGE_SECONDS:
        raise ValueError("Invalid session lifetime")
    now = int(time.time() if now is None else now)
    data = {"aud": AUDIENCE, "sub": subject, "school": school, "iat": now, "exp": now + ttl}
    if session_epoch is not None:
        if type(session_epoch) is not int or session_epoch < 0:
            raise ValueError("Invalid session epoch")
        data["epoch"] = session_epoch
    body = _b64(json.dumps(data, sort_keys=True, separators=(",", ":")).encode())
    mac = _b64(hmac.new(secret, body.encode("ascii"), hashlib.sha256).digest())
    return body + "." + mac

def verify_session(token, *, secret, now=None, expected_epoch=None):
    """Return a scoped principal only for a valid server-signed token."""
    _validate_secret(secret)
    if not isinstance(token, str) or len(token) > 4096 or token.count(".") != 1:
        raise PermissionError("Invalid session")
    try:
        body, signature = token.split(".")
        expected = hmac.new(secret, body.encode("ascii"), hashlib.sha256).digest()
        received = _unb64(signature)
        if not hmac.compare_digest(received, expected):
            raise PermissionError("Invalid session signature")
        payload = json.loads(_unb64(body))
        now = int(time.time() if now is None else now)
        if set(payload) not in ({"aud", "sub", "school", "iat", "exp"}, {"aud", "sub", "school", "iat", "exp", "epoch"}):
            raise PermissionError("Invalid session claims")
        if "epoch" in payload and (type(payload["epoch"]) is not int or payload["epoch"] < 0):
            raise PermissionError("Invalid session epoch")
        if expected_epoch is not None:
            if type(expected_epoch) is not int or expected_epoch < 0 or payload.get("epoch", 0) != expected_epoch:
                raise PermissionError("Revoked session")
        if payload["aud"] != AUDIENCE:
            raise PermissionError("Wrong session audience")
        if type(payload["iat"]) is not int or type(payload["exp"]) is not int:
            raise PermissionError("Invalid session timestamps")
        if not payload["iat"] <= now < payload["exp"] or payload["exp"] - payload["iat"] > MAX_AGE_SECONDS:
            raise PermissionError("Expired or future session")
        if any(not isinstance(payload[k], str) or not payload[k].strip() for k in ("sub", "school")):
            raise PermissionError("Missing session scope")
        return Principal(subject=payload["sub"], school=payload["school"], verified=True)
    except (ValueError, TypeError, UnicodeError, KeyError) as exc:
        raise PermissionError("Invalid session") from exc
