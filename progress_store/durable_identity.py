"""Synthetic-only durable enrollment and single-use recovery.

No HTTP endpoints, provider connection, real pupil data, or production credentials.
Store session signing keys outside SQLite. A real deployment requires audit,
identity governance, rate limiting, backup, consent and secure key rotation.
"""
import hashlib
import hmac
import secrets
import sqlite3
import time
from .approval_evidence import VerifiedDecision
from .session_auth import issue_test_session

def create_identity_schema(db):
    db.execute("""CREATE TABLE IF NOT EXISTS synthetic_enrollments (
      school TEXT NOT NULL, subject TEXT NOT NULL,
      reviewer_id TEXT NOT NULL, approved_at INTEGER NOT NULL,
      session_epoch INTEGER NOT NULL DEFAULT 0,
      PRIMARY KEY(school,subject))""")
    db.execute("""CREATE TABLE IF NOT EXISTS synthetic_recovery (
      school TEXT NOT NULL, subject TEXT NOT NULL,
      challenge_hash BLOB NOT NULL, expires_at INTEGER NOT NULL,
      PRIMARY KEY(school,subject),
      FOREIGN KEY(school,subject) REFERENCES synthetic_enrollments(school,subject))""")
    db.execute("""CREATE TABLE IF NOT EXISTS synthetic_recovery_attempts (
      school TEXT NOT NULL, subject TEXT NOT NULL,
      failures INTEGER NOT NULL DEFAULT 0,
      locked_until INTEGER NOT NULL DEFAULT 0,
      PRIMARY KEY(school,subject))""")
    db.commit()

class DurableSyntheticIdentity:
    def __init__(self, db, verifier, *, provider_id, reviewers, signing_key, clock=None):
        if not callable(verifier) or not provider_id or not reviewers:
            raise ValueError("Trusted provider and reviewers required")
        if not isinstance(signing_key,bytes) or len(signing_key)<32:
            raise ValueError("Strong server signing key required")
        self.db, self.verifier, self.provider_id = db, verifier, provider_id
        self.reviewers=frozenset(reviewers)
        self.signing_key=signing_key
        self.clock=clock or time.time

    def _approval(self, assertion, kind, subject, school):
        decision=self.verifier(assertion)
        if (not isinstance(decision,VerifiedDecision) or decision.approved is not True or
            decision.kind!=kind or decision.subject!=subject or decision.school!=school or
            not decision.decision_id or decision.reviewer_id not in self.reviewers):
            raise PermissionError("Invalid independent approval")
        return decision

    def _redeem(self, decision, kind, subject, school):
        self.db.execute("INSERT INTO redeemed_approvals VALUES (?,?,?,?,?)",
          (self.provider_id,decision.decision_id,kind,school,subject))

    def enroll(self, assertion, *, subject, school):
        decision=self._approval(assertion,"enrollment",subject,school)
        try:
            self.db.execute("BEGIN IMMEDIATE")
            self._redeem(decision,"enrollment",subject,school)
            self.db.execute("INSERT INTO synthetic_enrollments (school,subject,reviewer_id,approved_at) VALUES (?,?,?,?)",
                            (school,subject,decision.reviewer_id,int(self.clock())))
            self.db.commit()
        except sqlite3.IntegrityError as exc:
            self.db.rollback()
            raise PermissionError("Enrollment or approval already used") from exc
        except Exception:
            self.db.rollback()
            raise

    def issue(self, *, subject, school):
        row=self.db.execute("SELECT session_epoch FROM synthetic_enrollments WHERE school=? AND subject=?",
                            (school,subject)).fetchone()
        if row is None:
            raise PermissionError("Unapproved learner")
        return issue_test_session(subject=subject,school=school,secret=self.signing_key,
                                  now=int(self.clock()),session_epoch=row[0])

    def begin_recovery(self, assertion, *, subject, school):
        decision=self._approval(assertion,"recovery",subject,school)
        secret=secrets.token_urlsafe(32)
        digest=hmac.new(self.signing_key,secret.encode(),hashlib.sha256).digest()
        try:
            self.db.execute("BEGIN IMMEDIATE")
            if not self.db.execute("SELECT 1 FROM synthetic_enrollments WHERE school=? AND subject=?",
                                   (school,subject)).fetchone():
                raise PermissionError("Unapproved learner")
            self._redeem(decision,"recovery",subject,school)
            # Starting a new approved recovery invalidates a prior challenge.
            self.db.execute("""INSERT INTO synthetic_recovery VALUES (?,?,?,?)
              ON CONFLICT(school,subject) DO UPDATE SET
              challenge_hash=excluded.challenge_hash, expires_at=excluded.expires_at""",
              (school,subject,digest,int(self.clock())+600))
            self.db.commit()
        except sqlite3.IntegrityError as exc:
            self.db.rollback()
            raise PermissionError("Approval already used") from exc
        except Exception:
            self.db.rollback()
            raise
        return secret

    def _register_failed_recovery(self, *, subject, school, now):
        self.db.execute("""INSERT INTO synthetic_recovery_attempts
          (school,subject,failures,locked_until) VALUES (?,?,1,0)
          ON CONFLICT(school,subject) DO UPDATE SET failures=failures+1""",
          (school,subject))
        failures=self.db.execute("SELECT failures FROM synthetic_recovery_attempts WHERE school=? AND subject=?",
                                 (school,subject)).fetchone()[0]
        if failures>=5:
            self.db.execute("UPDATE synthetic_recovery_attempts SET locked_until=? WHERE school=? AND subject=?",
                            (now+900,school,subject))

    def complete_recovery(self, *, subject, school, challenge):
        if not isinstance(challenge,str) or not challenge or len(challenge)>256:
            raise PermissionError("Invalid recovery challenge")
        try:
            self.db.execute("BEGIN IMMEDIATE")
            now=int(self.clock())
            state=self.db.execute("SELECT failures,locked_until FROM synthetic_recovery_attempts WHERE school=? AND subject=?",
                                  (school,subject)).fetchone()
            if state and now < state[1]:
                raise PermissionError("Recovery temporarily locked")
            if state and state[1] and now>=state[1]:
                self.db.execute("DELETE FROM synthetic_recovery_attempts WHERE school=? AND subject=?",(school,subject))
            record=self.db.execute("SELECT challenge_hash,expires_at FROM synthetic_recovery WHERE school=? AND subject=?",
                                   (school,subject)).fetchone()
            digest=hmac.new(self.signing_key,challenge.encode(),hashlib.sha256).digest()
            if not record or now>=record[1] or not hmac.compare_digest(digest,record[0]):
                self._register_failed_recovery(subject=subject,school=school,now=now)
                self.db.commit()
                raise PermissionError("Invalid or expired recovery")
            self.db.execute("DELETE FROM synthetic_recovery WHERE school=? AND subject=?",(school,subject))
            self.db.execute("DELETE FROM synthetic_recovery_attempts WHERE school=? AND subject=?",(school,subject))
            self.db.execute("UPDATE synthetic_enrollments SET session_epoch=session_epoch+1 WHERE school=? AND subject=?",
                            (school,subject))
            epoch=self.db.execute("SELECT session_epoch FROM synthetic_enrollments WHERE school=? AND subject=?",
                                  (school,subject)).fetchone()[0]
            token=issue_test_session(subject=subject,school=school,secret=self.signing_key,now=now,session_epoch=epoch)
            self.db.commit()
            return token
        except Exception:
            if self.db.in_transaction:
                self.db.rollback()
            raise
