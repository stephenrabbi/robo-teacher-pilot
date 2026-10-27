"""Explicitly opt-in synthetic-only HTTP smoke service.

No enrollment, credentials or tokens accepted. Never mounted by live classroom.
A private staging gateway must control external access independently.
"""
from fastapi import FastAPI

def build_synthetic_identity_smoke_app(*, enabled=False):
    if not enabled:
        raise RuntimeError("Identity smoke service disabled")
    app=FastAPI(title="Disposable Identity Readiness",docs_url=None,redoc_url=None,openapi_url=None)
    @app.get("/internal/synthetic-identity/health")
    def health():
        return {"synthetic_only":True,"identity_endpoints_enabled":False}
    return app
