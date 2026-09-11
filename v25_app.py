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


def _inject_scripts(html, scripts):
    tags = [f'<script src="/classroom/{script}?v=freeze-diag-1"></script>' for script in scripts]
    return html.replace("</body>", "  " + "\n  ".join(tags) + "\n</body>")


@app.get("/classroom-app-base")
def classroom_app_base():
    """Serve raw classroom HTML without dynamically injected enhancements."""
    return HTMLResponse(_raw_classroom_html())


@app.get("/classroom-app-core-diagnostic")
def classroom_app_core_diagnostic():
    """Load only the two pre-redesign daily-learning enhancement scripts."""
    html = _inject_scripts(
        _raw_classroom_html(),
        ("daily_session.js", "daily_guidance_fix.js"),
    )
    return HTMLResponse(html)


@app.get("/classroom-app-ui-half-a")
def classroom_app_ui_half_a():
    """Load core daily scripts plus the first half of the redesign enhancements."""
    html = _inject_scripts(
        _raw_classroom_html(),
        (
            "daily_session.js",
            "daily_guidance_fix.js",
            "navigation_redesign.js",
            "avatar_layout.js",
            "state_feedback.js",
            "accessibility_tuning.js",
            "learner_home.js",
            "practice_layout.js",
            "canvas_hierarchy.js",
            "progress_layout.js",
        ),
    )
    return HTMLResponse(html)


@app.get("/classroom-app-ui-half-b")
def classroom_app_ui_half_b():
    """Load core daily scripts plus the second half of the redesign enhancements."""
    html = _inject_scripts(
        _raw_classroom_html(),
        (
            "daily_session.js",
            "daily_guidance_fix.js",
            "welcome_layout.js",
            "practice_feedback.js",
            "home_navigation.js",
            "data_saver.js",
            "friendly_errors.js",
            "ui_localization.js",
            "design_tokens.js",
        ),
    )
    return HTMLResponse(html)


@app.get("/classroom-app-ui-b1")
def classroom_app_ui_b1():
    """Load core daily scripts plus the first subgroup from the failing second half."""
    html = _inject_scripts(
        _raw_classroom_html(),
        (
            "daily_session.js",
            "daily_guidance_fix.js",
            "welcome_layout.js",
            "practice_feedback.js",
            "home_navigation.js",
            "data_saver.js",
        ),
    )
    return HTMLResponse(html)


@app.get("/classroom-app-ui-b1a")
def classroom_app_ui_b1a():
    """Load core daily scripts plus welcome/practice feedback only."""
    html = _inject_scripts(
        _raw_classroom_html(),
        (
            "daily_session.js",
            "daily_guidance_fix.js",
            "welcome_layout.js",
            "practice_feedback.js",
        ),
    )
    return HTMLResponse(html)


# Keep every normal staging route identical to production.
app.mount("/", shared_app)
