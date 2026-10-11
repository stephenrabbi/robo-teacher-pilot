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
