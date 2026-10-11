"""Synthetic-only durable single-use approval boundary.

Uses SQLite unique keys for atomic replay rejection across workers/restarts.
No public route, real provider integration or production pupil identities.
"""
import sqlite3
from .approval_evidence import VerifiedDecision
from .enrollment_gateway import ApprovedEnrollment

def create_approval_schema(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS redeemed_approvals (
        provider_id TEXT NOT NULL,
        decision_id TEXT NOT NULL,
        kind TEXT NOT NULL CHECK(kind IN ('enrollment','recovery')),
        school TEXT NOT NULL,
        subject TEXT NOT NULL,
        PRIMARY KEY(provider_id,decision_id)
    )""")
    conn.commit()

class DurableApprovalGate:
    def __init__(self, connection, verifier, gateway, *, provider_id):
        if not callable(verifier) or not isinstance(provider_id,str) or not provider_id.strip():
            raise ValueError("Trusted verifier and provider ID required")
        self.db, self.verifier, self.gateway, self.provider_id = connection, verifier, gateway, provider_id

    def _redeem(self, assertion, *, kind, school, subject):
        # Assertion verification is mandatory. Never trust caller-provided decisions.
        decision = self.verifier(assertion)
        if (not isinstance(decision, VerifiedDecision) or decision.approved is not True
                or decision.kind != kind or decision.school != school
                or decision.subject != subject or not decision.decision_id.strip()
                or not decision.reviewer_id.strip()):
            raise PermissionError("Approval scope mismatch")
        try:
            # BEGIN IMMEDIATE gives SQLite a write lock before checking eligibility.
            # Roll back the replay record if the subsequent gateway refuses approval.
            self.db.execute("BEGIN IMMEDIATE")
            self.db.execute(
                "INSERT INTO redeemed_approvals VALUES (?,?,?,?,?)",
                (self.provider_id,decision.decision_id,kind,school,subject))
            if kind == "enrollment":
                self.gateway.approve(
                    ApprovedEnrollment(subject,school,decision.decision_id,decision.reviewer_id),
                    authenticated_reviewer=decision.reviewer_id)
            else:
                # This only authorises a later recovery challenge; no token is issued.
                self.gateway.issue(subject=subject, school=school)
                if decision.reviewer_id not in self.gateway._reviewers:
                    raise PermissionError("Untrusted reviewer")
            self.db.commit()
        except sqlite3.IntegrityError as exc:
            self.db.rollback()
            raise PermissionError("Approval already used") from exc
        except Exception:
            self.db.rollback()
            raise
        return True

    def enroll(self, assertion, *, school, subject):
        return self._redeem(assertion,kind="enrollment",school=school,subject=subject)

    def authorize_recovery(self, assertion, *, school, subject):
        return self._redeem(assertion,kind="recovery",school=school,subject=subject)
