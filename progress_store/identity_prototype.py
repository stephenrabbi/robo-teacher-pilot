"""Synthetic-only identity issuance and recovery contract.

This module is NOT exposed through HTTP and must not be used to enrol children
without verified school/guardian authority. Recovery secrets are never logged.
"""
from dataclasses import dataclass
import hashlib
import hmac
import secrets
import time

from .session_auth import issue_test_session

@dataclass(frozen=True)
class Enrollment:
    subject: str
    school: str
    approved: bool

class TestIdentityAuthority:
    """Volatile test authority; deliberately not a production credential store."""
    def __init__(self, signing_key):
        if not isinstance(signing_key, bytes) or len(signing_key) < 32:
            raise ValueError("Strong server-held signing key required")
        self._key = signing_key
        self._enrollments = {}
        self._recovery = {}

    def register_approved(self, *, subject, school, approved):
        if not approved or not subject or not school:
            raise PermissionError("Verified enrollment approval is required")
        self._enrollments[(school, subject)] = Enrollment(subject, school, True)

    def create_recovery_challenge(self, *, subject, school, approved_recovery, now=None):
        if not approved_recovery or (school, subject) not in self._enrollments:
            raise PermissionError("Recovery approval required")
        now = int(time.time() if now is None else now)
        secret = secrets.token_urlsafe(32)
        digest = hmac.new(self._key, secret.encode(), hashlib.sha256).digest()
        self._recovery[(school, subject)] = (digest, now + 600)
        return secret

    def redeem_recovery(self, *, subject, school, challenge, now=None):
        now = int(time.time() if now is None else now)
        state = self._recovery.pop((school, subject), None)
        if state is None or not isinstance(challenge, str):
            raise PermissionError("Invalid recovery")
        digest, expiry = state
        actual = hmac.new(self._key, challenge.encode(), hashlib.sha256).digest()
        if now >= expiry or not hmac.compare_digest(digest, actual):
            raise PermissionError("Expired or invalid recovery")
        # Legacy synthetic recovery only; never exposed to live application.
        if (school, subject) not in self._enrollments:
            raise PermissionError("Unapproved learner")
        return issue_test_session(subject=subject, school=school, secret=self._key, now=now)
