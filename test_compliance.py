"""Static privacy/accessibility regression checks for Robo-Teacher."""
from pathlib import Path
from sheet_logger import _minimise_text

ROOT = Path(__file__).parent
index = (ROOT / "classroom" / "index.html").read_text(encoding="utf-8")
css = (ROOT / "classroom" / "styles.css").read_text(encoding="utf-8")
compliance = (ROOT / "classroom" / "compliance.js").read_text(encoding="utf-8")

for path in [
    "privacy.html",
    "terms-of-use.html",
    "terms-and-conditions.html",
    "cookie-policy.html",
    "refund-policy.html",
]:
    assert (ROOT / "classroom" / path).exists(), path

assert 'id="learnerConsent"' in index
assert 'Privacy Policy' in index
assert 'Cookie Policy' in index
assert 'Refund Policy' in index
assert 'for="practiceAnswer"' in index
assert 'for="question"' in index
assert 'id="clearQuestion"' in index
assert 'id="clearPracticeAnswer"' in index
assert 'referrerpolicy="no-referrer"' in index
assert 'sandbox=' in index
assert "externalContentAllowed" in compliance
assert "Clear this device data" in compliance
assert "Essential only" in compliance
assert "#0757c9" in css

sample = "Email me at child@example.com or +2348012345678, @sampleuser https://example.com"
redacted = _minimise_text(sample)
assert "child@example.com" not in redacted
assert "8012345678" not in redacted
assert "@sampleuser" not in redacted
assert "https://example.com" not in redacted

def luminance(hex_color):
    h = hex_color.lstrip("#")
    rgb = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    def channel(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = map(channel, rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def ratio(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)

assert ratio("#0757c9", "#ffffff") >= 4.5
print("Compliance/accessibility checks passed.")
