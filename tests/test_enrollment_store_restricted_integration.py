"""Offline integration coverage: restricted DB factory + enrollment store.

Fake SQL responses, not a real Supabase PostgreSQL session.
"""
import unittest
from datetime import datetime
from uuid import uuid4
from private_test_enrollment_store import PrivateTestEnrollmentStore
from staging_role_scoped_connection import build_test_connection_factory

DSN=("postgresql://robo_test_staging_login.drzaxpofuhqchmpkwhpy:placeholder@"
     "aws-1-eu-west-1.pooler.supabase.com:5432/postgres?sslmode=verify-full")


class Cursor:
    def __init__(self, db):
        self.db=db
        self.row=None
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def execute(self, sql, params=None):
        if sql=="SELECT current_user, session_user":
            self.row=(self.db.role,"robo_test_staging_login")
        elif sql=="SET LOCAL ROLE robo_test_enrollment_executor":
            self.db.role="robo_test_enrollment_executor"
        elif sql.startswith("INSERT INTO robo_test_private.enrollment_challenges"):
            assert self.db.role=="robo_test_enrollment_executor"
            uid,digest,expiry=params
            assert isinstance(expiry,datetime)
            self.db.challenge=(uid,digest)
        elif sql.startswith("SELECT robo_test_private.consume_and_enroll("):
            assert self.db.role=="robo_test_enrollment_executor"
            if self.db.challenge==params and not self.db.consumed:
                self.db.consumed=True
                self.row=(self.db.cloud_id,)
            else:
                self.row=(None,)
        else:
            raise AssertionError("Unexpected SQL operation")
    def fetchone(self): return self.row


class Conn:
    def __init__(self,db):
        self.db=db
        self.db.role="robo_test_staging_login"
    def __enter__(self): return self
    def __exit__(self,*a): return False
    def cursor(self): return Cursor(self.db)


class FakeDB:
    challenge=None
    consumed=False
    role="robo_test_staging_login"
    def __init__(self):
        self.cloud_id=str(uuid4())
    def connect(self,dsn):
        assert dsn==DSN
        return Conn(self)


class TestStoreIntegration(unittest.TestCase):
    def test_issue_consume_and_reject_replay(self):
        db=FakeDB()
        store=PrivateTestEnrollmentStore(
            build_test_connection_factory(db.connect,DSN))
        uid=str(uuid4())
        digest=b"q"*32
        store.create(uid,digest,300)
        self.assertEqual(store.consume_and_enroll(uid,digest),db.cloud_id)
        self.assertIsNone(store.consume_and_enroll(uid,digest))

    def test_different_user_cannot_claim_challenge(self):
        db=FakeDB()
        store=PrivateTestEnrollmentStore(
            build_test_connection_factory(db.connect,DSN))
        owner=str(uuid4())
        store.create(owner,b"r"*32,300)
        self.assertIsNone(store.consume_and_enroll(str(uuid4()),b"r"*32))
        self.assertEqual(store.consume_and_enroll(owner,b"r"*32),db.cloud_id)


if __name__=="__main__":
    unittest.main()
