"""Synthetic-only enrollment authorization gate. No routes, storage or token issuance.

Approvals here are test fixtures, NOT verified real school or guardian consent.
"""
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class SyntheticDecision:
    learner_ref: str
    school_ref: str
    issuer_ref: str
    purpose: str
    approved: bool
    expires_at: datetime

class SyntheticEnrollmentGate:
    def __init__(self, *, authorized_school_reviewers, authorized_guardian_reviewers):
        self.school_reviewers=frozenset(authorized_school_reviewers)
        self.guardian_reviewers=frozenset(authorized_guardian_reviewers)
        if not self.school_reviewers or not self.guardian_reviewers:
            raise ValueError("Both reviewer lists are mandatory")

    def evaluate(self, *, learner_ref, school_ref, school_decision, guardian_decision, now=None):
        now=now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            raise ValueError("Timezone-aware evaluation required")
        if not learner_ref or not school_ref or not isinstance(learner_ref,str) or not isinstance(school_ref,str):
            raise PermissionError("Invalid enrollment scope")
        for decision, purpose, reviewers in (
            (school_decision,"school_eligibility",self.school_reviewers),
            (guardian_decision,"guardian_authorization",self.guardian_reviewers),
        ):
            if not isinstance(decision,SyntheticDecision):
                raise PermissionError("Missing independent decision")
            if (decision.learner_ref!=learner_ref or decision.school_ref!=school_ref
                or decision.purpose!=purpose or decision.issuer_ref not in reviewers
                or not decision.approved or decision.expires_at.tzinfo is None
                or decision.expires_at<=now):
                raise PermissionError("Enrollment denied")
        return True
