"""Isolated staging health probe. No enrollment endpoints, no DSN logging."""
import logging
import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from staging_restricted_db_probe import check_restricted_connection

logger = logging.getLogger("robo-teacher-staging-probe")
app = FastAPI(title="Robo-Teacher restricted DB probe",docs_url=None,redoc_url=None,openapi_url=None)


def safe_failure_category(exc):
    """Never expose raw driver errors; they can include connection details."""
    if isinstance(exc, ValueError):
        return "configuration_rejected"
    if isinstance(exc, RuntimeError):
        return "role_or_permission_check_failed"
    code = getattr(exc, "sqlstate", None)
    if code in ("28P01", "28000"):
        return "database_authentication_failed"
    if code == "42501":
        return "database_permission_denied"
    name = type(exc).__name__
    if name == "OperationalError":
        # Driver details intentionally suppressed, including TLS/network text.
        return "database_transport_or_tls_or_auth_failed"
    if name in ("ImportError", "ModuleNotFoundError"):
        return "database_driver_missing"
    return "unexpected_probe_failure"


@app.get("/health")
def health():
    dsn=os.environ.get("ROBO_TEST_DATABASE_URL")
    if os.environ.get("ROBO_TEST_PROBE_ENABLED")!="true" or not dsn:
        return JSONResponse({"status":"not_configured"},status_code=503)
    try:
        import psycopg
        check_restricted_connection(psycopg.connect,dsn)
    except Exception as exc:
        logger.warning("Restricted staging probe: %s",safe_failure_category(exc))
        return JSONResponse({"status":"restricted_connection_failed"},status_code=503)
    return {"status":"restricted_connection_verified"}
