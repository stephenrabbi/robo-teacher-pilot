"""Unmounted guarded test router: integrates origin/rate guard into HTTP path.

In-memory rate-limits are test-only. Not wired into main.py.
"""
from fastapi import APIRouter, Header, HTTPException
from supabase_test_enrollment_service import EnrollBody, EnrollmentService
from enrollment_request_guard import EnrollmentRequestGuard


def make_guarded_test_enrollment_router(service: EnrollmentService,
                                         guard: EnrollmentRequestGuard):
    router=APIRouter(prefix="/api/internal/supabase-enrollment-test")
    def checked(authorization: str, origin: str, action: str):
        # Never accept browser-supplied user IDs; token verified first.
        uid=service.authenticate(authorization)
        guard.enforce(origin=origin,verified_user_id=uid,action=action)

    @router.post("/issue")
    def issue(authorization: str=Header(default=""),origin: str=Header(default="")):
        checked(authorization,origin,"issue")
        return service.issue(authorization)

    @router.post("/complete")
    def complete(body: EnrollBody,authorization: str=Header(default=""),
                 origin: str=Header(default="")):
        checked(authorization,origin,"complete")
        return service.consume(authorization,body.challenge)
    return router
