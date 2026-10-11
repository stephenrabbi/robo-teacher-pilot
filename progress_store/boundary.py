"""Test-only boundary between signed sessions and the isolated progress store.

No HTTP routes or live datastore. The caller cannot supply an owner/school scope;
those are obtained exclusively from a verified signed session.
"""
from .session_auth import verify_session
from .prototype import list_events, record_event

class ProgressBoundary:
    def __init__(self, connection, signing_key):
        self._db = connection
        self._key = signing_key

    def submit(self, *, bearer_token, event, now=None):
        principal = verify_session(bearer_token, secret=self._key, now=now)
        return record_event(self._db, principal, event)

    def history(self, *, bearer_token, now=None):
        principal = verify_session(bearer_token, secret=self._key, now=now)
        return list_events(self._db, principal)

    def _enrolled_principal(self, token, enrollment_connection):
        if enrollment_connection is not self._db:
            raise RuntimeError("Atomic authorization requires the same SQLite connection")
        principal = verify_session(token, secret=self._key)
        row = self._db.execute(
            "SELECT session_epoch FROM synthetic_enrollments WHERE school=? AND subject=?",
            (principal.school,principal.subject)).fetchone()
        if row is None:
            raise PermissionError("Unenrolled learner")
        verify_session(token, secret=self._key, expected_epoch=row[0])
        return principal

    def submit_enrolled(self, *, bearer_token, event, enrollment_connection):
        """Serialize enrollment validation and write against the recovery lock."""
        if enrollment_connection is not self._db:
            raise RuntimeError("Atomic authorization requires the same SQLite connection")
        self._db.execute("BEGIN IMMEDIATE")
        try:
            principal=self._enrolled_principal(bearer_token,enrollment_connection)
            result=record_event(self._db,principal,event)
            # record_event commits via its own context manager.
            if self._db.in_transaction:
                self._db.commit()
            return result
        except Exception:
            if self._db.in_transaction:
                self._db.rollback()
            raise

    def history_enrolled(self, *, bearer_token, enrollment_connection):
        if enrollment_connection is not self._db:
            raise RuntimeError("Atomic authorization requires the same SQLite connection")
        self._db.execute("BEGIN IMMEDIATE")
        try:
            principal=self._enrolled_principal(bearer_token,enrollment_connection)
            rows=list_events(self._db,principal)
            self._db.commit()
            return rows
        except Exception:
            if self._db.in_transaction:
                self._db.rollback()
            raise
