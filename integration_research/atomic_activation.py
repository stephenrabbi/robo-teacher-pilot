"""Isolated, fail-closed atomic redemption prototype; not wired to live app.

The external verifier must authenticate and validate institutionally authorized,
scope-bound decisions. This module cannot itself establish guardian consent.
"""
import hashlib
import sqlite3
import threading

class AtomicSyntheticActivation:
    def __init__(self, connection, verify_decisions):
        if not isinstance(connection, sqlite3.Connection) or not callable(verify_decisions):
            raise ValueError("Explicit database and independent verifier required")
        self.db=connection
        self.verify=verify_decisions
        self.lock=threading.RLock()
        with self.db:
            self.db.execute("""CREATE TABLE IF NOT EXISTS atomic_test_approvals
                (proof_hash TEXT PRIMARY KEY, school TEXT NOT NULL, learner TEXT NOT NULL)""")
            self.db.execute("""CREATE TABLE IF NOT EXISTS atomic_test_accounts
                (school TEXT NOT NULL, learner TEXT NOT NULL, status TEXT NOT NULL,
                 PRIMARY KEY(school,learner))""")

    def activate(self, *, school, learner, approval_proof):
        if not isinstance(school,str) or not school or not isinstance(learner,str) or not learner:
            raise PermissionError("Invalid scope")
        # The verifier must be independent of caller-controlled approval booleans.
        if not isinstance(approval_proof,str) or not approval_proof:
            raise PermissionError("Invalid approval proof")
        with self.lock:
            self.db.execute("BEGIN IMMEDIATE")
            try:
                approved=self.verify(approval_proof,school,learner)
                if approved is not True:
                    raise PermissionError("Approval rejected")
                digest=hashlib.sha256(approval_proof.encode()).hexdigest()
                self.db.execute("INSERT INTO atomic_test_approvals VALUES (?,?,?)",
                                (digest,school,learner))
                self.db.execute("INSERT INTO atomic_test_accounts VALUES (?,?,'synthetic')",
                                (school,learner))
                self.db.commit()
            except sqlite3.IntegrityError as exc:
                self.db.rollback()
                raise PermissionError("Duplicate approval or account") from exc
            except BaseException:
                self.db.rollback()
                raise
            return True
