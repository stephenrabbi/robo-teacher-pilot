"""Offline regression tests for the Supabase isolation smoke-test verifier."""
import os
import unittest
from unittest.mock import patch
from tests import supabase_two_account_isolation as smoke

class FakeResponse:
    def __init__(self,value): self.value=value
    def raise_for_status(self): pass
    def json(self): return self.value

class FakeClient:
    def __init__(self,leak=False,empty=False): self.leak=leak;self.empty=empty
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def post(self,url,headers,json):
        who="a" if json["email"]=="a@example.test" else "b"
        return FakeResponse({"access_token":"token-"+who,"user":{"id":"uid-"+who}})
    def get(self,url,params,headers):
        who=headers["Authorization"].split("-")[-1]
        if self.empty:return FakeResponse([])
        owner="b" if self.leak and who=="a" else who
        return FakeResponse([{"user_id":"uid-"+owner}])

class SmokeTests(unittest.TestCase):
    def run_test(self,client):
        vals={"ROBO_TEST_SUPABASE_URL":"https://gpshctxxgjvzplrbegwf.supabase.co",
            "ROBO_TEST_SUPABASE_PUBLISHABLE_KEY":"test-publishable",
            "ROBO_TEST_USER_A_EMAIL":"a@example.test","ROBO_TEST_USER_A_PASSWORD":"fake-a",
            "ROBO_TEST_USER_B_EMAIL":"b@example.test","ROBO_TEST_USER_B_PASSWORD":"fake-b"}
        with patch.dict(os.environ,vals),patch.object(smoke.httpx,"Client",return_value=client):
            return smoke.main()
    def test_distinct_owner_rows_pass(self):self.assertEqual(self.run_test(FakeClient()),0)
    def test_cross_account_leak_fails(self):
        with self.assertRaises(RuntimeError):self.run_test(FakeClient(leak=True))
    def test_empty_fixtures_fail(self):
        with self.assertRaises(RuntimeError):self.run_test(FakeClient(empty=True))
    def test_missing_secrets_fail_closed(self):
        with patch.dict(os.environ,{},clear=True):self.assertEqual(smoke.main(),2)
if __name__=="__main__":unittest.main()
