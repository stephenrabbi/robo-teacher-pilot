"""Synthetic-only recovery gate. No public routes or real guardian verification."""
from dataclasses import dataclass
from datetime import datetime, timezone
from .provisioning_gate import SyntheticProvisioningGate

@dataclass(frozen=True)
class RecoveryApproval:
    learner_ref: str
    school_ref: str
    reviewer_ref: str
    expires_at: datetime
    approved: bool

class SyntheticRecoveryGate:
    def __init__(self, *, reviewers, verify_operator, audit_sink):
        self.reviewers=frozenset(reviewers)
        if not self.reviewers or not callable(verify_operator) or not callable(audit_sink):
            raise ValueError("Independent reviewers, operator verifier and audit required")
        self.verify_operator=verify_operator
        self.audit_sink=audit_sink

    def authorize(self, *, approval, operator_proof, now=None):
        now=now or datetime.now(timezone.utc)
        allowed=False
        try:
            if (not isinstance(approval, RecoveryApproval) or not approval.approved
                or not approval.learner_ref or not approval.school_ref
                or approval.reviewer_ref not in self.reviewers
                or approval.expires_at.tzinfo is None or approval.expires_at<=now):
                raise PermissionError("Recovery approval invalid")
            operator=self.verify_operator(operator_proof)
            if not isinstance(operator,str) or not operator or operator==approval.reviewer_ref:
                raise PermissionError("Independent operator required")
            allowed=True
            return (approval.school_ref,approval.learner_ref)
        finally:
            self.audit_sink({"action":"synthetic_recovery_authorization","allowed":allowed,
                             "time":now.isoformat()})
