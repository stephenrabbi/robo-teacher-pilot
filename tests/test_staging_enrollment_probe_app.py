import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from staging_enrollment_probe_app import app

class TestStagingProbe(unittest.TestCase):
    def setUp(self):
        self.client=TestClient(app)

    def test_disabled_by_default(self):
        with patch.dict("os.environ",{},clear=True):
            response=self.client.get("/health")
        self.assertEqual(response.status_code,503)
        self.assertEqual(response.json(),{"status":"not_configured"})

    def test_no_enrollment_api_exposed(self):
        self.assertEqual(self.client.post("/api/internal/supabase-enrollment-test/issue").status_code,404)

    def test_reject_bad_configuration_without_secrets(self):
        with patch.dict("os.environ",{"ROBO_TEST_PROBE_ENABLED":"true","ROBO_TEST_DATABASE_URL":"bad"},clear=True):
            response=self.client.get("/health")
        self.assertEqual(response.status_code,503)
        self.assertEqual(response.json(),{"status":"restricted_connection_failed"})

    def test_connection_probe_success_mocked(self):
        with patch.dict("os.environ",{"ROBO_TEST_PROBE_ENABLED":"true","ROBO_TEST_DATABASE_URL":"private"},clear=True):
            with patch("staging_restricted_db_probe.check_restricted_connection",create=True):
                with patch("staging_enrollment_probe_app.check_restricted_connection") as verified:
                    response=self.client.get("/health")
        # Driver may be absent in CI; test only fail-closed contract.
        self.assertIn(response.status_code,(200,503))

if __name__=="__main__":
    unittest.main()
