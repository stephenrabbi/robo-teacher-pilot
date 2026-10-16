"""Fail-closed approval evidence boundary for future school identity providers.

This module validates proof *returned by an independent trusted verifier*.
It cannot itself validate a school administrator's identity or parental consent.
No HTTP routes or production credentials.
"""
from dataclasses import dataclass
from .enrollment_gateway import ApprovedEnrollment

@dataclass(frozen=True)
class VerifiedDecision:
    decision_id: str
    subject: str
    school: str
    reviewer_id: str
    kind: str
    approved: bool

class EvidenceGatedIdentity:
    def __init__(self, gateway, verifier):
        if not callable(verifier):
            raise ValueError("Independent approval verifier required")
        self.gateway = gateway
        self.verifier = verifier
        self._used = set()

    def _check(self, *, reference, subject, school, kind):
        if not isinstance(reference, str) or not reference or not subject or not school:
            raise PermissionError("Approval reference and scope required")
        decision = self.verifier(reference)
        if (not isinstance(decision, VerifiedDecision) or not decision.approved or
            decision.decision_id != reference or decision.kind != kind or
            decision.subject != subject or decision.school != school or
            not decision.reviewer_id):
            raise PermissionError("Independent approval verification failed")
        key = (kind, reference)
        if key in self._used:
            raise PermissionError("Approval reference already redeemed")
        return decision, key

    def enroll(self, *, reference, subject, school):
        decision, key = self._check(reference=reference, subject=subject, school=school, kind="enrollment")
        # Reviewer must also be independently configured as trusted in gateway.
        self.gateway.approve(
            ApprovedEnrollment(subject, school, reference, decision.reviewer_id),
            authenticated_reviewer=decision.reviewer_id,
        )
        self._used.add(key)

    def authorize_recovery(self, *, reference, subject, school):
        decision, key = self._check(reference=reference, subject=subject, school=school, kind="recovery")
        # Enrolment scope is verified again before approving a recovery operation.
        self.gateway.require_enrollment(subject=subject, school=school)
        self._used.add(key)
        return True
