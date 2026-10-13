"""Isolated in-memory enrollment challenge proof-of-concept; NOT mounted.

Only newly created cloud enrollment is permitted; legacy data claims are excluded.
Production requires a durable transactional store, rate limits and guardian consent.
"""
import hashlib
import hmac
import secrets
import threading
import time
from dataclasses import dataclass


class EnrollmentDenied(PermissionError):
    pass


@dataclass(frozen=True)
class Challenge:
    owner: str
    digest: bytes
    expires_at: float


class TestOnlyEnrollmentChallenges:
    def __init__(self, clock=time.time, ttl_seconds=300):
        self._clock = clock
        self._ttl = ttl_seconds
        self._pending = {}
        self._lock = threading.Lock()

    def issue(self, verified_supabase_user_id: str):
        if not verified_supabase_user_id:
            raise EnrollmentDenied("Authenticated account required")
        ticket = secrets.token_urlsafe(32)
        digest = hashlib.sha256(ticket.encode("ascii")).digest()
        with self._lock:
            self._pending[digest] = Challenge(verified_supabase_user_id, digest, self._clock() + self._ttl)
        return ticket

    def consume(self, ticket: str, verified_supabase_user_id: str):
        if not isinstance(ticket, str) or not ticket or not verified_supabase_user_id:
            raise EnrollmentDenied("Enrollment proof required")
        digest = hashlib.sha256(ticket.encode("utf-8")).digest()
        with self._lock:
            challenge = self._pending.get(digest)
            if challenge is None or challenge.expires_at <= self._clock():
                raise EnrollmentDenied("Proof expired or used")
            if not hmac.compare_digest(challenge.owner, verified_supabase_user_id):
                raise EnrollmentDenied("Proof belongs to another account")
            del self._pending[digest]
        return "CLOUD-" + secrets.token_hex(16)
