import os
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from supabase_link_test_router import VerifyLinkRequest, verify_link


class TestDisabledSupabaseLinkEndpoint(unittest.TestCase):
    def setUp(self):
        self.request = VerifyLinkRequest(
            session_token="a" * 30, supabase_access_token="b" * 30)

    def test_disabled_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(HTTPException) as cm:
                verify_link(self.request)
            self.assertEqual(cm.exception.status_code, 404)

    def test_must_pin_testing_project(self):
        with patch.dict(os.environ, {
            "ROBO_SUPABASE_ACCOUNT_LINK_TEST_ENABLED": "yes",
            "ROBO_SUPABASE_TEST_PROJECT_URL": "https://gpshctxxgjvzplrbegwf.supabase.co",
            "ROBO_SUPABASE_TEST_PUBLISHABLE_KEY": "sb_publishable_sample",
        }, clear=True):
            with self.assertRaises(HTTPException) as cm:
                verify_link(self.request)
            self.assertEqual(cm.exception.status_code, 503)

    def test_invalid_credentials_rejected(self):
        with patch.dict(os.environ, {
            "ROBO_SUPABASE_ACCOUNT_LINK_TEST_ENABLED": "yes",
            "ROBO_SUPABASE_TEST_PROJECT_URL": "https://drzaxpofuhqchmpkwhpy.supabase.co",
            "ROBO_SUPABASE_TEST_PUBLISHABLE_KEY": "sb_publishable_sample",
        }, clear=True), patch("supabase_link_test_router._verify_session", side_effect=ValueError):
            with self.assertRaises(HTTPException) as cm:
                verify_link(self.request)
            self.assertEqual(cm.exception.status_code, 401)

    def test_success_is_verification_only(self):
        with patch.dict(os.environ, {
            "ROBO_SUPABASE_ACCOUNT_LINK_TEST_ENABLED": "yes",
            "ROBO_SUPABASE_TEST_PROJECT_URL": "https://drzaxpofuhqchmpkwhpy.supabase.co",
            "ROBO_SUPABASE_TEST_PUBLISHABLE_KEY": "sb_publishable_sample",
        }, clear=True), patch("supabase_link_test_router._verify_session", return_value="WEB-TEST"), patch(
            "supabase_link_test_router.verify_supabase_user",
            return_value="bc160d0f-acfb-4af6-9dd7-5aa6d468f5ae"):
            self.assertEqual(verify_link(self.request), {"verified": True, "linked": False, "persisted": False})


if __name__ == "__main__":
    unittest.main()
