"""Non-network regression guards for the optional Classroom 2.0 welcome refresh."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "classroom"


def test_welcome_refresh_stylesheet_is_loaded_after_existing_styles():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    base = html.index('/classroom/classroom2.css?v=')
    refresh = html.index('/classroom/classroom2-welcome-refresh.css?v=')
    assert base < refresh
    assert (ROOT / "classroom2-welcome-refresh.css").is_file()


def test_original_learning_entry_points_are_preserved():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    for element in (
        'id="learnerNickname"', 'id="learnerCode"',
        'id="generateLearnerCode"', 'id="learnerClass"',
        'id="learnerConsent"', 'id="startLearning"',
        'id="resumeLearning"', 'id="hearFounder"',
        'id="showTeacherLogin"', 'id="teacherAccessKey"',
    ):
        assert element in html
    for asset in (
        "robo-teacher-logo.png",
        "real-students-classroom-welcome.jpg",
        "herbert-stephen-founder.jpg",
    ):
        assert asset in html
    assert "a photo of a learning problem" in html


def test_refresh_scopes_most_rules_to_welcome_and_supports_accessibility():
    css = (ROOT / "classroom2-welcome-refresh.css").read_text(encoding="utf-8")
    assert "#welcome.welcome-screen" in css
    assert "prefers-reduced-motion:reduce" in css
    assert "focus-visible" in css
    assert "@media(max-width:600px)" in css
    assert "@media(max-width:900px)" in css
