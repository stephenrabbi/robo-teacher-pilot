import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from enrollment_request_guard import EnrollmentRequestGuard
from supabase_test_enrollment_service import EnrollmentService
from guarded_test_enrollment_router import make_guarded_test_enrollment_router


class Store:
    def __init__(self): self.pending={}; self.enrolled=set()
    def create(self,uid,digest,ttl_seconds): self.pending[digest]=uid
    def consume_and_enroll(self,uid,digest):
        if self.pending.get(digest)!=uid or uid in self.enrolled:return None
        self.pending.pop(digest);self.enrolled.add(uid);return "CLOUD-TEST"


class GuardedHTTPTest(unittest.TestCase):
    def setUp(self):
        self.store=Store()
        service=EnrollmentService(verify_token=lambda t:{"token-a":"user-a","token-b":"user-b"}.get(t),
                                  store=self.store)
        guard=EnrollmentRequestGuard("https://staging.example.org",max_calls=2)
        app=FastAPI()
        app.include_router(make_guarded_test_enrollment_router(service,guard))
        self.client=TestClient(app)
        self.url="/api/internal/supabase-enrollment-test"
    def headers(self,token="token-a",origin="https://staging.example.org"):
        return {"Authorization":"Bearer "+token,"Origin":origin}

    def test_full_flow_with_origin(self):
        issued=self.client.post(self.url+"/issue",headers=self.headers())
        self.assertEqual(issued.status_code,200)
        completed=self.client.post(self.url+"/complete",headers=self.headers(),
                                   json={"challenge":issued.json()["challenge"]})
        self.assertEqual(completed.status_code,200)

    def test_cross_origin_rejected(self):
        result=self.client.post(self.url+"/issue",headers=self.headers(origin="https://attacker.example"))
        self.assertEqual(result.status_code,403)
        self.assertEqual(len(self.store.pending),0)

    def test_rate_limit_enforced_through_route(self):
        for _ in range(2):
            self.assertEqual(self.client.post(self.url+"/issue",headers=self.headers()).status_code,200)
        result=self.client.post(self.url+"/issue",headers=self.headers())
        self.assertEqual(result.status_code,429)

    def test_auth_required_before_storage(self):
        result=self.client.post(self.url+"/issue",headers=self.headers(token="unverified"))
        self.assertEqual(result.status_code,401)
        self.assertEqual(len(self.store.pending),0)


if __name__=="__main__":unittest.main()
