import unittest
from supabase_session_binding_guard import create_verified_binding


class TestSessionBindingGuard(unittest.TestCase):
    def setUp(self):
        self.uid = "bc160d0f-acfb-4af6-9dd7-5aa6d468f5ae"
        self.verify_classroom = lambda token: "WEB-SYNTHETIC" if token == "valid-classroom-token" else None
        self.verify_supabase = lambda token: self.uid if token == "valid-supabase-token" else None

    def bind(self, **kwargs):
        data={"classroom_token": "valid-classroom-token",
              "supabase_access_token": "valid-supabase-token",
              "verify_classroom": self.verify_classroom,
              "verify_supabase": self.verify_supabase}
        data.update(kwargs)
        return create_verified_binding(**data)

    def test_both_verified_identities_required(self):
        record=self.bind()
        self.assertEqual(record.classroom_student_id,"WEB-SYNTHETIC")
        self.assertEqual(record.supabase_user_id,self.uid)

    def test_must_reject_wrong_classroom_session(self):
        with self.assertRaises(ValueError):
            self.bind(classroom_token="nickname-or-code")

    def test_must_reject_wrong_supabase_token(self):
        with self.assertRaises(ValueError):
            self.bind(supabase_access_token="IND-SYNTH-A")

    def test_no_client_selected_account_id_accepted(self):
        with self.assertRaises(TypeError):
            self.bind(user_id=self.uid)

    def test_malformed_authenticated_user_id_denied(self):
        with self.assertRaises(ValueError):
            self.bind(verify_supabase=lambda token:"not-a-uuid")


if __name__=="__main__":
    unittest.main()
