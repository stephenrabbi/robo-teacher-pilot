"""Fail-closed ownership gate for *new* cloud enrollment (not live-mounted).

A verified Supabase user plus an existing classroom HMAC session does NOT prove
ownership of legacy classroom progress: classroom identities can be reissued
from a school learner code or client-supplied learner key.

Only a separately validated one-time enrollment challenge may authorize a NEW
cloud identity association. Never transfer historical progress via this gate.
"""
from dataclasses import dataclass


class EnrollmentProofRequired(PermissionError):
    pass


@dataclass(frozen=True)
class VerifiedEnrollment:
    supabase_user_id: str
    newly_issued_cloud_identity: str


def authorize_new_cloud_enrollment(*, verified_supabase_user_id: str,
                                   verified_one_time_proof: str,
                                   validate_enrollment_proof) -> VerifiedEnrollment:
    if not isinstance(verified_supabase_user_id, str) or not verified_supabase_user_id:
        raise EnrollmentProofRequired("Verified Supabase user required")
    if not isinstance(verified_one_time_proof, str) or not verified_one_time_proof:
        raise EnrollmentProofRequired("New enrollment proof required")
    # Provided validator must be a trusted, server-side, one-time atomic verifier.
    # Never pass client-defined callable or accept learner code as proof.
    identity = validate_enrollment_proof(verified_one_time_proof, verified_supabase_user_id)
    if not isinstance(identity, str) or not identity.startswith("CLOUD-"):
        raise EnrollmentProofRequired("Invalid or consumed enrollment proof")
    return VerifiedEnrollment(verified_supabase_user_id, identity)


def authorize_legacy_progress_claim(*args, **kwargs):
    """Always deny attempts to claim historical data using legacy sessions."""
    raise EnrollmentProofRequired("Historical classroom progress cannot be claimed with a legacy session")
