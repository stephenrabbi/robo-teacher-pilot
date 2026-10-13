"""Isolated read-only database probe service; never mount enrollment APIs."""
import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from staging_restricted_db_probe import check_restricted_connection

app = FastAPI(title="Robo-Teacher restricted test DB probe", docs_url=None, redoc_url=None, openapi_url=None)

@app.get("/health")
def health():
    dsn=os.environ.get("ROBO_TEST_DATABASE_URL")
    enabled=os.environ.get("ROBO_TEST_PROBE_ENABLED") == "true"
    if not enabled or not dsn:
        return JSONResponse({"status":"not_configured"}, status_code=503)
    try:
        import psycopg
        check_restricted_connection(psycopg.connect,dsn)
    except Exception:
        return JSONResponse({"status":"restricted_connection_failed"},status_code=503)
    return {"status":"restricted_connection_verified"}
