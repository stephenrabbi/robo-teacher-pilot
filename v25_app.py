"""Backward-compatible Robo-Teacher V2.5 staging entrypoint.

The classroom API is registered by ``main`` so production and staging expose
the same browser endpoints. Staging may continue to run this module.
"""
from pathlib import Path

from fastapi import Request
from fastapi.responses import HTMLResponse

from main import app

_CLASSROOM_INDEX = Path(__file__).resolve().parent / "classroom" / "index.html"
_DAILY_SESSION_SCRIPT = '<script src="/classroom/daily_session.js?v=20260910-daily-session1"></script>'


@app.middleware("http")
async def _load_daily_session_progress(request: Request, call_next):
    """Attach the staging-only daily-session progress layer to the classroom."""
    if request.method == "GET" and request.url.path.rstrip("/") == "/classroom-app":
        html = _CLASSROOM_INDEX.read_text(encoding="utf-8")
        if "daily_session.js" not in html:
            html = html.replace("</body>", f"  {_DAILY_SESSION_SCRIPT}\n</body>")
        return HTMLResponse(html)
    return await call_next(request)
