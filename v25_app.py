"""Robo-Teacher V2.5 staging entrypoint.

This composes the stable V2 application with the browser classroom API without
changing the production uvicorn entrypoint (main:app). Staging should run:
    uvicorn v25_app:app --host 0.0.0.0 --port $PORT
"""
from main import app
from classroom_api import router as classroom_router

app.include_router(classroom_router)
