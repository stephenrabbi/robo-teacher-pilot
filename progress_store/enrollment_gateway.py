"""Test-only verified enrollment boundary for learner progress.

Trusted operator approvals must be checked by an external real-world workflow.
This component cannot validate school or guardian authority on its own.
"""
from dataclasses import dataclass
import hmac
from .identity_prototype import TestIdentityAuthority

@dataclass(frozen=True)
class ApprovedEnrollment:
    subject: str
    school: str
    approval_ref: str
    reviewer_id: str

class VerifiedEnrollmentGateway:
    """In-memory synthetic enrollment gate, not wired to public routes."""
    def __init__(self, signing_key, trusted_reviewers):
        if not trusted_reviewers:
            raise ValueError("At least one trusted reviewer required")
        self._authority = TestIdentityAuthority(signing_key)
        self._reviewers = frozenset(trusted_reviewers)
        self._approved = set()

    def approve(self, enrollment, *, authenticated_reviewer):
        if not isinstance(enrollment, ApprovedEnrollment):
            raise PermissionError("Structured approval required")
        if authenticated_reviewer not in self._reviewers or not hmac.compare_digest(
            enrollment.reviewer_id, authenticated_reviewer
        ):
            raise PermissionError("Reviewer not authorized")
        if not enrollment.approval_ref.strip() or not enrollment.subject.strip() or not enrollment.school.strip():
            raise PermissionError("Incomplete enrollment approval")
        key = (enrollment.school, enrollment.subject)
        self._approved.add(key)
        self._authority.register_approved(subject=enrollment.subject, school=enrollment.school, approved=True)

