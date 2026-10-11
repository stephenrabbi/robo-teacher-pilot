"""Opt-in, standalone ASGI API for synthetic progress testing only.

Not imported/mounted by main.py or v25_app.py. No public enrollment or
token-issuance endpoints. Disabled by default; never point it at pupil data.
"""
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal
from datetime import datetime
from uuid import UUID
import sqlite3

from .boundary import ProgressBoundary
from .prototype import create_schema

class ProgressEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    event_id: UUID
    event_type: Literal["practice_completed", "diagnostic_completed", "revision_completed"]
    class_level: Literal["JSS1", "JSS2", "JSS3"]
    topic_key: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    correct: int = Field(ge=0, le=100)
    total: int = Field(ge=0, le=100)
    occurred_at: datetime

def build_synthetic_progress_app(*, enabled=False, signing_key=None, connection=None):
    """Explicitly injectable test dependencies; no production defaults."""
    if not enabled:
        raise RuntimeError("Synthetic progress API is disabled")
    if not isinstance(signing_key, bytes) or len(signing_key) < 32:
        raise ValueError("Test signing secret required")
    if connection is None:
        raise ValueError("An isolated synthetic database connection is required")
    create_schema(connection)
    boundary = ProgressBoundary(connection, signing_key)
    app = FastAPI(title="Synthetic Robo-Teacher Progress API", docs_url=None, redoc_url=None, openapi_url=None)

    def token_from_header(authorization):
        if not authorization or not authorization.startswith("Bearer ") or len(authorization) > 4096:
            raise HTTPException(status_code=401, detail="Authentication required")
        return authorization[7:]

    @app.post("/internal/synthetic-progress/events", status_code=201)
    def save(event: ProgressEvent, authorization: str | None = Header(default=None)):
        try:
            payload = event.model_dump(mode="json")
            inserted = boundary.submit(bearer_token=token_from_header(authorization), event=payload)
            return {"recorded": inserted}
        except PermissionError:
            raise HTTPException(status_code=401, detail="Invalid session")
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid progress event")

    @app.get("/internal/synthetic-progress/events")
    def history(authorization: str | None = Header(default=None)):
        try:
            rows = boundary.history(bearer_token=token_from_header(authorization))
            return {"events": [
                dict(zip(("event_id","event_type","class_level","topic_key","correct","total","occurred_at"), row))
                for row in rows
            ]}
        except PermissionError:
            raise HTTPException(status_code=401, detail="Invalid session")

    return app
