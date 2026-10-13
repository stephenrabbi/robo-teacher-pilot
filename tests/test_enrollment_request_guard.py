import unittest
from fastapi import HTTPException
from enrollment_request_guard import EnrollmentRequestGuard


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.now=[20.]
        self.guard=EnrollmentRequestGuard("https://staging.example.org",
                                         clock=lambda:self.now[0],max_calls=2,window=60)

    def call(self,origin="https://staging.example.org",user="user-a",action="issue"):
        self.guard.enforce(origin=origin,verified_user_id=user,action=action)

    def test_allows_limited_same_origin_calls(self):
        self.call()
        self.call()

    def test_throttles_excessive_calls(self):
        self.call()
        self.call()
        with self.assertRaises(HTTPException) as cm:self.call()
        self.assertEqual(cm.exception.status_code,429)

    def test_recovers_after_window(self):
        self.call()
        self.call()
        self.now[0]+=60
        self.call()

    def test_other_origin_denied(self):
        with self.assertRaises(HTTPException) as cm:
            self.call(origin="https://attacker.example")
        self.assertEqual(cm.exception.status_code,403)

    def test_missing_verified_user_denied(self):
        with self.assertRaises(HTTPException) as cm:
            self.call(user="")
        self.assertEqual(cm.exception.status_code,401)

    def test_separate_users_and_actions(self):
        self.call()
        self.call()
        self.call(user="user-b")
        self.call(action="complete")


if __name__=="__main__":
    unittest.main()
