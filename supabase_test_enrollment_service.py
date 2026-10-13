"""Unmounted test enrollment API. Not registered with main.py.

Authenticated user IDs are derived server-side. Storage is an injected trusted
adapter; this module does not grant database access or mount HTTP routes.
"""
import hashlib
import secrets
from dataclasses import dataclass
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field


@dataclass
class EnrollmentService:
    verify_token: object
    store: object

    def authenticate(self, authorization: str) -> str:
        prefix = "Bearer "
        if not isinstance(authorization, str) or not authorization.startswith(prefix):
            raise HTTPException(status_code=401, detail="Authentication required")
        token = authorization[len(prefix):]
        if not token or len(token) > 8192:
            raise HTTPException(status_code=401, detail="Authentication required")
        try:
            user_id = self.verify_token(token)
        except Exception as exc:
            raise HTTPException(status_code=401, detail="Authentication failed") from exc
        if not isinstance(user_id, str) or not user_id:
            raise HTTPException(status_code=401, detail="Authentication failed")
        return user_id

    def issue(self, authorization: str) -> dict:
        uid = self.authenticate(authorization)
        raw = secrets.token_urlsafe(32)
        digest = hashlib.sha256(raw.encode("ascii")).digest()
        # Trusted store must persist digest and owner with TTL; never plaintext.
        self.store.create(uid, digest, ttl_seconds=300)
        return {"challenge": raw, "expires_in": 300}

    def consume(self, authorization: str, proof: str) -> dict:
        uid = self.authenticate(authorization)
        if not isinstance(proof, str) or not 20 <= len(proof) <= 256:
            raise HTTPException(status_code=400, detail="Invalid challenge")
        digest = hashlib.sha256(proof.encode("utf-8")).digest()
        # Trusted store must atomically consume proof and create new cloud
        # identity; no historical WEB-* account records may be claimed.
        cloud_id = self.store.consume_and_enroll(uid, digest)
        if cloud_id is None:
            raise HTTPException(status_code=409, detail="Challenge rejected")
        return {"enrolled": True, "cloud_identity_created": True}


class EnrollBody(BaseModel):
    challenge: str = Field(min_length=20, max_length=256)


def make_test_enrollment_router(service: EnrollmentService) -> APIRouter:
    router = APIRouter(prefix="/api/internal/supabase-enrollment-test")
    @router.post("/issue")
    def issue(authorization: str = Header(default="")):
        return service.issue(authorization)
    @router.post("/complete")
    def complete(body: EnrollBody, authorization: str = Header(default="")):
        return service.consume(authorization, body.challenge)
    return router
