"""Unmounted test-only enrollment request guard.

Production would require shared durable rate limits across workers, verified
proxy information, strong CSRF/session protections, and centralized monitoring.
"""
import time
from collections import defaultdict, deque
from fastapi import HTTPException


class EnrollmentRequestGuard:
    def __init__(self, allowed_origin: str, *, clock=time.monotonic, max_calls=5, window=60):
        if not allowed_origin.startswith("https://") or allowed_origin.endswith("/"):
            raise ValueError("Explicit HTTPS origin required")
        self.allowed_origin=allowed_origin
        self.clock=clock
        self.max_calls=max_calls
        self.window=window
        self.buckets=defaultdict(deque)

    def enforce(self, *, origin: str, verified_user_id: str, action: str):
        # Same-origin checks mitigate browser-initiated cross-site requests,
        # not server-to-server abuse. Authentication is still mandatory.
        if origin != self.allowed_origin:
            raise HTTPException(status_code=403,detail="Origin not allowed")
        if not verified_user_id or action not in ("issue","complete"):
            raise HTTPException(status_code=401,detail="Authenticated account required")
        now=self.clock()
        bucket=self.buckets[(verified_user_id,action)]
        while bucket and now-bucket[0]>=self.window:
            bucket.popleft()
        if len(bucket)>=self.max_calls:
            raise HTTPException(status_code=429,detail="Too many enrollment requests")
        bucket.append(now)
