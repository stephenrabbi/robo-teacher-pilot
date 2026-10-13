import unittest
from supabase_enrollment_ownership_gate import (
    EnrollmentProofRequired, authorize_new_cloud_enrollment, authorize_legacy_progress_claim)


class TestEnrollmentOwnershipGate(unittest.TestCase):
    def test_new_verified_one_time_enrollment(self):
        def validator(proof, user):
            return "CLOUD-FRESH-1" if proof == "fresh-proof" and user == "signed-in-user" else None
        result = authorize_new_cloud_enrollment(
            verified_supabase_user_id="signed-in-user",
            verified_one_time_proof="fresh-proof",
            validate_enrollment_proof=validator)
        self.assertEqual(result.newly_issued_cloud_identity, "CLOUD-FRESH-1")

    def test_legacy_code_is_not_proof(self):
        with self.assertRaises(EnrollmentProofRequired):
            authorize_new_cloud_enrollment(
                verified_supabase_user_id="signed-in-user",
                verified_one_time_proof="ISE-JSS2-001",
                validate_enrollment_proof=lambda proof, user: None)

    def test_session_is_not_proof_of_historical_ownership(self):
        with self.assertRaises(EnrollmentProofRequired):
            authorize_legacy_progress_claim(session_token="valid-signed-session",
                                            verified_supabase_user_id="signed-in-user")

    def test_invalid_proof_denied(self):
        with self.assertRaises(EnrollmentProofRequired):
            authorize_new_cloud_enrollment(
                verified_supabase_user_id="signed-in-user",
                verified_one_time_proof="used-proof",
                validate_enrollment_proof=lambda proof, user: None)

    def test_missing_supabase_user_denied(self):
        with self.assertRaises(EnrollmentProofRequired):
            authorize_new_cloud_enrollment(
                verified_supabase_user_id="", verified_one_time_proof="fresh-proof",
                validate_enrollment_proof=lambda proof, user: "CLOUD-FRESH-1")


if __name__ == "__main__":
    unittest.main()
