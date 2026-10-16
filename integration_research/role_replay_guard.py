"""Disposable SQLite replay tracker for synthetic role assertions only.

No production identity, no public routes. Consume a verified assertion once
inside a transaction; share one database between workers in synthetic tests.
"""
import sqlite3
import threading
import hashlib

class SyntheticRoleReplayGuard:
    def __init__(self, connection):
        if not isinstance(connection, sqlite3.Connection):
            raise ValueError("Explicit disposable SQLite connection required")
        self.db=connection
        self.lock=threading.RLock()
        with self.lock,self.db:
            self.db.execute("""CREATE TABLE IF NOT EXISTS synthetic_role_redemptions(
                assertion_hash TEXT PRIMARY KEY, actor TEXT NOT NULL)""")

    def verify_once(self, verifier, proof):
        if not callable(verifier):
            raise ValueError("Role verifier required")
        with self.lock:
            actor=verifier(proof)
            if actor is None:
                return None
            fingerprint=hashlib.sha256(proof.encode("utf-8")).hexdigest()
            try:
                with self.db:
                    self.db.execute("INSERT INTO synthetic_role_redemptions VALUES (?,?)",
                                    (fingerprint,actor))
            except sqlite3.IntegrityError:
                return None
            return actor
