"""Fail-closed Supabase classroom account link test route.

Not registered in main.py or mounted by the live classroom. Requires an explicit
future review before enabling. Never stores a user binding or learner record.
"""
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from classroom_api import _verify_session
from supabase_remote_user_verifier import verify_supabase_user, SupabaseAuthVerificationError
from supabase_session_binding_guard import create_verified_binding

router = APIRouter(prefix="/api/classroom/supabase-test", tags=["supabase-test"])


class VerifyLinkRequest(BaseModel):
    session_token: str = Field(min_length=20, max_length=300)
    supabase_access_token: str = Field(min_length=20, max_length=8192)


@router.post("/verify-link")
def verify_link(request: VerifyLinkRequest):
    # Never enable via client-provided inputs.
    if os.getenv("ROBO_SUPABASE_ACCOUNT_LINK_TEST_ENABLED", "").lower() != "yes":
        raise HTTPException(status_code=404, detail="Not available")
    url = os.getenv("ROBO_SUPABASE_TEST_PROJECT_URL", "")
    key = os.getenv("ROBO_SUPABASE_TEST_PUBLISHABLE_KEY", "")
    # Defense against accidentally connecting this experimental endpoint to production.
    if url.rstrip("/") != "https://drzaxpofuhqchmpkwhpy.supabase.co":
        raise HTTPException(status_code=503, detail="Test project not configured")
    try:
        binding = create_verified_binding(
            classroom_token=request.session_token,
            supabase_access_token=request.supabase_access_token,
            verify_classroom=_verify_session,
            verify_supabase=lambda token: verify_supabase_user(
                token, project_url=url, publishable_key=key),
        )
    except (ValueError, SupabaseAuthVerificationError):
        raise HTTPException(status_code=401, detail="Account verification failed")
    # Do not return identifiers or tokens in this pre-integration endpoint.
    return {"verified": True, "linked": False, "persisted": False}
