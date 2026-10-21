"""Browser smoke checks for the isolated Classroom 2.0 welcome visual update."""
import contextlib
import functools
import http.server
import socketserver
import threading
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

class WelcomeBrowserQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
        cls.httpd = Server(("127.0.0.1", 0), handler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True, args=["--no-sandbox"])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def test_welcome_at_viewport_sizes(self):
        for width, height in ((320, 750), (375, 812), (768, 1024), (1366, 900)):
            with self.subTest(width=width):
                page = self.browser.new_page(viewport={"width": width, "height": height})
                try:
                    page.goto(f"http://127.0.0.1:{self.port}/classroom/index.html", wait_until="domcontentloaded")
                    page.locator("#welcome").wait_for(state="visible", timeout=10000)
                    self.assertTrue(page.locator("#learnerNickname").count())
                    self.assertTrue(page.locator("#learnerConsent").count())
                    self.assertTrue(page.locator("#startLearning").is_visible())
                    self.assertTrue(page.locator("#hearFounder").is_visible())
                    self.assertTrue(page.locator(".student-welcome-photo img").evaluate("(el) => el.complete && el.naturalWidth > 0"))
                    self.assertTrue(page.locator(".founder-avatar").first.evaluate("(el) => el.complete && el.naturalWidth > 0"))
                    sizes = page.evaluate("({ viewport: document.documentElement.clientWidth, scroll: document.documentElement.scrollWidth })")
                    self.assertLessEqual(sizes["scroll"], sizes["viewport"] + 2, sizes)
                    page.screenshot(path=f"/tmp/classroom2-welcome-{width}.png", full_page=True)
                finally:
                    page.close()

    def test_onboarding_required_permission(self):
        page = self.browser.new_page(viewport={"width": 375, "height": 812})
        try:
            page.goto(f"http://127.0.0.1:{self.port}/classroom/index.html", wait_until="domcontentloaded")
            page.locator("#learnerNickname").fill("Test Learner")
            page.locator("#learnerConsent").uncheck()
            page.locator("#startLearning").click()
            self.assertTrue(page.locator("#welcome").is_visible(), "Without consent learner must not enter classroom")
        finally:
            page.close()

    def test_generate_learner_code_and_valid_onboarding(self):
        page = self.browser.new_page(viewport={"width": 375, "height": 812})
        try:
            page.goto(f"http://127.0.0.1:{self.port}/classroom/index.html", wait_until="domcontentloaded")
            page.locator("#generateLearnerCode").click()
            code = page.locator("#learnerCode").input_value()
            self.assertTrue(code.strip(), "Generate a code must populate learner code")
            page.locator("#learnerNickname").fill("Test Learner")
            page.locator("#learnerConsent").check()
            page.locator("#startLearning").click()
            page.locator("#classroom").wait_for(state="visible", timeout=10000)
            self.assertFalse(page.locator("#welcome").is_visible())
        finally:
            page.close()

    def test_hear_herbert_button_interaction(self):
        page = self.browser.new_page(viewport={"width": 375, "height": 812})
        try:
            page.goto(f"http://127.0.0.1:{self.port}/classroom/index.html", wait_until="domcontentloaded")
            page.locator("#hearFounder").click()
            self.assertTrue(page.locator("#welcome").is_visible())
            self.assertTrue(page.locator("#hearFounder").count())
            # Actual audible output and avatar frame switching require device testing.
        finally:
            page.close()

if __name__ == "__main__":
    unittest.main()
