"""Test-only DB-API adapter for private Supabase enrollment operations.

UNMOUNTED. Caller supplies a separately secured PostgreSQL connection factory.
Never expose connection credentials, SQL functions, or account IDs to browsers.
"""
from datetime import datetime, timedelta, timezone
from uuid import UUID


class PrivateTestEnrollmentStore:
    def __init__(self, connect):
        self._connect = connect

    @staticmethod
    def _uid(user_id):
        try:
            normalized = str(UUID(str(user_id)))
        except (TypeError, ValueError, AttributeError) as exc:
            raise ValueError("Verified user UUID required") from exc
        if normalized != str(user_id).lower():
            raise ValueError("Canonical user UUID required")
        return normalized

    @staticmethod
    def _digest(digest):
        if not isinstance(digest, bytes) or len(digest) != 32:
            raise ValueError("SHA-256 digest required")
        return digest

    def create(self, user_id, digest, ttl_seconds):
        uid = self._uid(user_id)
        self._digest(digest)
        if not isinstance(ttl_seconds, int) or not 30 <= ttl_seconds <= 300:
            raise ValueError("Invalid TTL")
        expiration = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO robo_test_private.enrollment_challenges "
                    "(user_id,proof_digest,expires_at) VALUES (%s,%s,%s)",
                    (uid, digest, expiration),
                )

    def consume_and_enroll(self, user_id, digest):
        uid = self._uid(user_id)
        self._digest(digest)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT robo_test_private.consume_and_enroll(%s,%s)",
                    (uid, digest),
                )
                row = cur.fetchone()
        return str(row[0]) if row and row[0] else None
