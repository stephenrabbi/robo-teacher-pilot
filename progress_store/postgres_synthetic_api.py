"""Opt-in PostgreSQL-only synthetic progress API, not mounted by live classroom."""
from datetime import datetime
from typing import Literal
from uuid import UUID
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from .postgres_adapter import SyntheticPostgresProgress

class EventInput(BaseModel):
    model_config=ConfigDict(extra="forbid")
    event_id: UUID
    event_type: Literal["practice_completed","diagnostic_completed","revision_completed"]
    class_level: Literal["JSS1","JSS2","JSS3"]
    topic_key: str=Field(min_length=1,max_length=80,pattern=r"^[A-Za-z0-9_-]+$")
    correct: int=Field(ge=0,le=100)
    total: int=Field(ge=0,le=100)
    occurred_at: datetime

def build_postgres_synthetic_api(*, enabled=False, connection_factory=None, signing_key=None):
    if not enabled:
        raise RuntimeError("PostgreSQL synthetic API disabled")
    if not callable(connection_factory):
        raise ValueError("Disposable connection factory required")
    storage=SyntheticPostgresProgress(connection_factory,signing_key)
    app=FastAPI(title="Isolated Synthetic PostgreSQL Progress",docs_url=None,redoc_url=None,openapi_url=None)

    def bearer(auth):
        if not isinstance(auth,str) or not auth.startswith("Bearer ") or len(auth)>4096:
            raise HTTPException(status_code=401,detail="Authentication required")
        return auth[7:]

    @app.post("/internal/synthetic-postgres/events",status_code=201)
    def save(event:EventInput,authorization:str|None=Header(default=None)):
        try:
            return {"recorded":storage.write(bearer_token=bearer(authorization),event=event.model_dump(mode="json"))}
        except PermissionError:
            raise HTTPException(status_code=401,detail="Invalid session")
        except ValueError:
            raise HTTPException(status_code=422,detail="Invalid progress event")

    @app.get("/internal/synthetic-postgres/events")
    def history(authorization:str|None=Header(default=None)):
        try:
            rows=storage.history(bearer_token=bearer(authorization))
            return {"events":[dict(zip(("event_id","event_type","class_level","topic_key","correct","total","occurred_at"),
                (str(r[0]),*r[1:6],r[6].isoformat()))) for r in rows]}
        except PermissionError:
            raise HTTPException(status_code=401,detail="Invalid session")
    return app
