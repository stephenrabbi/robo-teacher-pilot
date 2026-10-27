import unittest
from progress_store.enrollment_gateway import ApprovedEnrollment, VerifiedEnrollmentGateway
from progress_store.session_auth import verify_session

KEY = b"synthetic-identity-gateway-signing-secret-0001"

class EnrollmentGatewayTests(unittest.TestCase):
    def setUp(self):
        self.gateway = VerifiedEnrollmentGateway(KEY, {"reviewer-1"})

    def test_unauthorized_reviewer_cannot_approve(self):
        enrollment = ApprovedEnrollment("learner-A", "school-one", "approval-123", "reviewer-1")
        with self.assertRaises(PermissionError):
            self.gateway.approve(enrollment, authenticated_reviewer="outsider")

    def test_enrollment_review_does_not_issue_session(self):
        self.gateway.approve(
            ApprovedEnrollment("learner-A", "school-one", "approval-123", "reviewer-1"),
            authenticated_reviewer="reviewer-1",
        )
        self.assertIn(("school-one", "learner-A"), self.gateway._approved)
        self.assertFalse(hasattr(self.gateway, "issue"))
        self.assertFalse(hasattr(self.gateway._authority, "issue_for_approved"))

    def test_missing_reference_denied(self):
        with self.assertRaises(PermissionError):
            self.gateway.approve(ApprovedEnrollment("learner-A", "school-one", "", "reviewer-1"), authenticated_reviewer="reviewer-1")

if __name__ == "__main__":
    unittest.main()
