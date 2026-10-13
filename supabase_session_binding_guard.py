"""Prototype fail-closed identity binding guard (NOT wired to the live app).

All identity verification must occur in a trusted backend: verify classroom HMAC
and Supabase JWT (issuer, audience, signature, expiry) before invoking this helper.
A caller-supplied learner code or nickname is never sufficient for ownership.
"""
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class VerifiedBinding:
    classroom_student_id: str
    supabase_user_id: str


def create_verified_binding(*, classroom_token: str, supabase_access_token: str,
                            verify_classroom, verify_supabase) -> VerifiedBinding:
    if not isinstance(classroom_token, str) or not classroom_token:
        raise ValueError("Classroom authentication required")
    if not isinstance(supabase_access_token, str) or not supabase_access_token:
        raise ValueError("Supabase authentication required")
    # The verifier functions must be supplied by trusted server infrastructure,
    # never from a request payload. Their outputs must be independently verified.
    student_id = verify_classroom(classroom_token)
    user_id = verify_supabase(supabase_access_token)
    if not isinstance(student_id, str) or not student_id.startswith("WEB-"):
        raise ValueError("Invalid verified classroom identity")
    try:
        canonical_uuid = str(UUID(str(user_id)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError("Invalid verified Supabase identity") from exc
    if canonical_uuid != str(user_id).lower():
        raise ValueError("Noncanonical Supabase identity")
    return VerifiedBinding(classroom_student_id=student_id, supabase_user_id=canonical_uuid)
