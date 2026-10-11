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

    def test_unapproved_learner_cannot_get_token(self):
        with self.assertRaises(PermissionError):
            self.gateway.issue(subject="learner-A", school="school-one", now=1000)

    def test_approved_subject_can_get_scoped_token(self):
        enrollment = ApprovedEnrollment("learner-A", "school-one", "approval-123", "reviewer-1")
        self.gateway.approve(enrollment, authenticated_reviewer="reviewer-1")
        token = self.gateway.issue(subject="learner-A", school="school-one", now=1000)
        principal = verify_session(token, secret=KEY, now=1001)
        self.assertEqual((principal.subject, principal.school), ("learner-A", "school-one"))

    def test_approval_does_not_cross_school_or_subject(self):
        self.gateway.approve(ApprovedEnrollment("learner-A", "school-one", "approval-123", "reviewer-1"), authenticated_reviewer="reviewer-1")
        for subject, school in [("learner-B", "school-one"), ("learner-A", "school-two")]:
            with self.assertRaises(PermissionError):
                self.gateway.issue(subject=subject, school=school, now=1000)

    def test_missing_reference_denied(self):
        with self.assertRaises(PermissionError):
            self.gateway.approve(ApprovedEnrollment("learner-A", "school-one", "", "reviewer-1"), authenticated_reviewer="reviewer-1")

if __name__ == "__main__":
    unittest.main()
