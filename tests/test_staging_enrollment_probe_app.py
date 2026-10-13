import sys
import types
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from staging_enrollment_probe_app import app


class TestStagingProbe(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_disabled_by_default(self):
        with patch.dict("os.environ", {}, clear=True):
            response = self.client.get("/health")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"status": "not_configured"})

    def test_no_enrollment_api_exposed(self):
        self.assertEqual(
            self.client.post("/api/internal/supabase-enrollment-test/issue").status_code, 404
        )

    def test_reject_bad_configuration_without_secrets(self):
        environment = {"ROBO_TEST_PROBE_ENABLED": "true", "ROBO_TEST_DATABASE_URL": "bad"}
        with patch.dict("os.environ", environment, clear=True):
            response = self.client.get("/health")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"status": "restricted_connection_failed"})

    def test_connection_probe_success_mocked(self):
        environment = {"ROBO_TEST_PROBE_ENABLED": "true", "ROBO_TEST_DATABASE_URL": "private"}
        driver = types.ModuleType("psycopg")
        driver.connect = lambda dsn: None
        with patch.dict("sys.modules", {"psycopg": driver}):
            with patch.dict("os.environ", environment, clear=True):
                with patch("staging_enrollment_probe_app.check_restricted_connection") as verify:
                    response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "restricted_connection_verified"})
        verify.assert_called_once_with(driver.connect, "private")


if __name__ == "__main__":
    unittest.main()
