"""Backward-compatible Robo-Teacher V2.5 staging entrypoint.

The classroom API and classroom page are registered by ``main`` so production
and staging exercise the same application path. This staging module also exposes
a temporary base-page diagnostic route that serves the raw classroom without
injected enhancement scripts. It is used only to isolate frontend freezes.
"""

from fastapi.responses import HTMLResponse

from main import app


@app.get("/classroom-app-base")
def classroom_app_base():
    """Serve the raw classroom HTML for staging-only frontend isolation."""
    with open("classroom/index.html", "r", encoding="utf-8") as classroom_file:
        return HTMLResponse(classroom_file.read())
