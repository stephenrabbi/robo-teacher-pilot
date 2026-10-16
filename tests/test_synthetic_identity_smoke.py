import unittest
from fastapi.testclient import TestClient
from integration_research.smoke_api import build_synthetic_identity_smoke_app

class SyntheticSmokeTests(unittest.TestCase):
    def test_disabled_by_default_and_no_learner_routes(self):
        with self.assertRaises(RuntimeError):
            build_synthetic_identity_smoke_app()
        app=build_synthetic_identity_smoke_app(enabled=True)
        with TestClient(app) as client:
            response=client.get("/internal/synthetic-identity/health")
            self.assertEqual(response.status_code,200)
            self.assertEqual(response.json(),{"synthetic_only":True,"identity_endpoints_enabled":False})
            for method in (client.get,client.post):
                self.assertEqual(method("/internal/synthetic-identity/learner").status_code,404)
                self.assertEqual(method("/internal/synthetic-identity/enroll").status_code,404)
                self.assertEqual(method("/internal/synthetic-identity/recovery").status_code,404)

if __name__=="__main__":
    unittest.main()
