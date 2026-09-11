"""Backward-compatible Robo-Teacher V2.5 staging entrypoint.

Production and staging still exercise the same ``main`` application.  This
wrapper adds one staging-only diagnostic route before mounting the shared app,
so the diagnostic cannot be shadowed by routes registered in ``main``.
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from main import app as shared_app


app = FastAPI(title="Robo-Teacher V2.5 Staging")


@app.get("/classroom-app-base")
def classroom_app_base():
    """Serve raw classroom HTML without the dynamically injected UI scripts."""
    with open("classroom/index.html", "r", encoding="utf-8") as classroom_file:
        return HTMLResponse(classroom_file.read())


# Keep every normal staging route identical to production.
app.mount("/", shared_app)
