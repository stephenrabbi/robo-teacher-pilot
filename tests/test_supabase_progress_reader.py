import os
import unittest
from unittest.mock import patch
from integration_research.supabase_progress_reader import read_own_progress, PROJECT_URL

class FakeResponse:
    def raise_for_status(self):pass
    def __init__(self,body):self.body=body
    def json(self):return self.body
class FakeClient:
    def __init__(self):self.calls=[]
    def get(self,*args,**kwargs):
        self.calls.append((args,kwargs))
        return FakeResponse({"id":"synthetic-test-user"} if args[0].endswith("/auth/v1/user") else [{"topic_code":"fractions","mastery_score":70,"updated_at":"2026-10-11T00:00:00Z"}])

class ReaderTests(unittest.TestCase):
    def test_disabled_even_with_key_and_token(self):
        with patch.dict(os.environ,{"ROBO_SUPABASE_LEARNER_READ_ENABLED":"false",
            "ROBO_SUPABASE_PUBLISHABLE_KEY":"sb_publishable_dummy"}):
            with self.assertRaises(PermissionError):
                read_own_progress("x"*40,enabled=True)
    def test_missing_token_denied(self):
        with patch.dict(os.environ,{"ROBO_SUPABASE_LEARNER_READ_ENABLED":"true",
                "ROBO_SUPABASE_PUBLISHABLE_KEY":"sb_publishable_dummy"}):
            with self.assertRaises(PermissionError):read_own_progress("",enabled=True)
    def test_secret_key_denied(self):
        with patch.dict(os.environ,{"ROBO_SUPABASE_LEARNER_READ_ENABLED":"true",
                "ROBO_SUPABASE_PUBLISHABLE_KEY":"sb_secret_forbidden"}):
            with self.assertRaises(RuntimeError):read_own_progress("x"*40,enabled=True)
    def test_missing_identity_fails_without_progress_request(self):
        class NoIdentity(FakeClient):
            def get(self,*args,**kwargs):
                self.calls.append((args,kwargs))
                return FakeResponse({})
        c=NoIdentity()
        with patch.dict(os.environ,{"ROBO_SUPABASE_LEARNER_READ_ENABLED":"true",
                "ROBO_SUPABASE_PUBLISHABLE_KEY":"sb_publishable_dummy"}):
            with self.assertRaises(PermissionError):
                read_own_progress("x"*40,enabled=True,client=c)
        self.assertEqual(len(c.calls),1)

    def test_invalid_progress_payload_is_rejected(self):
        class InvalidProgress(FakeClient):
            def get(self,*args,**kwargs):
                self.calls.append((args,kwargs))
                return FakeResponse({"id":"synthetic-test-user"} if args[0].endswith("/auth/v1/user") else {"error":"unexpected"})
        with patch.dict(os.environ,{"ROBO_SUPABASE_LEARNER_READ_ENABLED":"true",
                "ROBO_SUPABASE_PUBLISHABLE_KEY":"sb_publishable_dummy"}):
            with self.assertRaises(RuntimeError):
                read_own_progress("x"*40,enabled=True,client=InvalidProgress())

    def test_calls_user_token_no_privileged_owner_filter(self):
        c=FakeClient()
        with patch.dict(os.environ,{"ROBO_SUPABASE_LEARNER_READ_ENABLED":"true",
                "ROBO_SUPABASE_PUBLISHABLE_KEY":"sb_publishable_dummy"}):
            self.assertEqual(len(read_own_progress("x"*40,enabled=True,client=c)),1)
        args,opts=c.calls[0]
        self.assertEqual(args[0],PROJECT_URL+"/auth/v1/user")
        args,opts=c.calls[1]
        self.assertEqual(args[0],PROJECT_URL+"/rest/v1/robo_learning_progress")
        self.assertEqual(opts["headers"]["Authorization"],"Bearer "+"x"*40)
        self.assertEqual(opts["headers"]["apikey"],"sb_publishable_dummy")
        self.assertNotIn("user_id",opts["params"])
if __name__=="__main__":unittest.main()
