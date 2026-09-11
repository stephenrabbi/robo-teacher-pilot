"""Backward-compatible Robo-Teacher V2.5 staging entrypoint.

Production and staging still exercise the same ``main`` application. This
wrapper exposes staging-only diagnostic routes before mounting the shared app,
so frontend freezes can be isolated without touching production.
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from main import app as shared_app


app = FastAPI(title="Robo-Teacher V2.5 Staging")


def _raw_classroom_html():
    with open("classroom/index.html", "r", encoding="utf-8") as classroom_file:
        return classroom_file.read()


@app.get("/classroom-app-base")
def classroom_app_base():
    """Serve raw classroom HTML without dynamically injected enhancements."""
    return HTMLResponse(_raw_classroom_html())


@app.get("/classroom-app-core-diagnostic")
def classroom_app_core_diagnostic():
    """Load only the two pre-redesign daily-learning enhancement scripts."""
    html = _raw_classroom_html()
    scripts = (
        '<script src="/classroom/daily_session.js?v=diag-core-1"></script>',
        '<script src="/classroom/daily_guidance_fix.js?v=diag-core-1"></script>',
    )
    html = html.replace("</body>", "  " + "\n  ".join(scripts) + "\n</body>")
    return HTMLResponse(html)


# Keep every normal staging route identical to production.
app.mount("/", shared_app)
