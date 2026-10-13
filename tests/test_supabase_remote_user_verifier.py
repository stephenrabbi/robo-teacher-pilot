import io
import json
import unittest
from supabase_remote_user_verifier import verify_supabase_user, SupabaseAuthVerificationError

URL="https://drzaxpofuhqchmpkwhpy.supabase.co"
KEY="sb_publishable_testing"
UID="bc160d0f-acfb-4af6-9dd7-5aa6d468f5ae"

class Response:
    status=200
    def __init__(self,data): self.data=data
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def read(self,n): return self.data

class TestSupabaseRemoteVerifier(unittest.TestCase):
    def test_valid_remote_user(self):
        def provider(req,timeout):
            self.assertEqual(req.full_url,URL+"/auth/v1/user")
            self.assertTrue(req.headers["Authorization"].startswith("Bearer "))
            return Response(json.dumps({"id":UID}).encode())
        self.assertEqual(verify_supabase_user("t"*32,project_url=URL,publishable_key=KEY,urlopen=provider),UID)

    def test_reject_unsupported_project(self):
        with self.assertRaises(SupabaseAuthVerificationError):
            verify_supabase_user("t"*32,project_url="https://example.com",publishable_key=KEY)

    def test_reject_token_without_remote_identity(self):
        with self.assertRaises(SupabaseAuthVerificationError):
            verify_supabase_user("t"*32,project_url=URL,publishable_key=KEY,urlopen=lambda req,timeout:Response(b'{"id":"learner-code"}'))

    def test_reject_missing_token(self):
        with self.assertRaises(SupabaseAuthVerificationError):
            verify_supabase_user("",project_url=URL,publishable_key=KEY)

if __name__=="__main__":
    unittest.main()
