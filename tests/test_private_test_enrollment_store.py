import unittest
from contextlib import contextmanager
from uuid import UUID
from private_test_enrollment_store import PrivateTestEnrollmentStore


class FakeCursor:
    def __init__(self, statements): self.statements=statements
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def execute(self,sql,params): self.statements.append((sql,params))
    def fetchone(self): return (UUID("0aa5e893-ac14-4b0b-9025-f08d8f7f6ba8"),)


class FakeConnection:
    def __init__(self,statements): self.statements=statements
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def cursor(self): return FakeCursor(self.statements)


class TestPrivateEnrollmentStore(unittest.TestCase):
    def setUp(self):
        self.statements=[]
        self.store=PrivateTestEnrollmentStore(lambda: FakeConnection(self.statements))
        self.uid="bc160d0f-acfb-4af6-9dd7-5aa6d468f5ae"
        self.digest=b"x"*32

    def test_create_uses_bound_parameters_not_sql_interpolation(self):
        self.store.create(self.uid,self.digest,300)
        sql,params=self.statements[0]
        self.assertIn("VALUES (%s,%s,%s)",sql)
        self.assertEqual(params[0],self.uid)
        self.assertEqual(params[1],self.digest)

    def test_consume_uses_private_transactional_function(self):
        result=self.store.consume_and_enroll(self.uid,self.digest)
        sql,params=self.statements[0]
        self.assertIn("robo_test_private.consume_and_enroll(%s,%s)",sql)
        self.assertEqual(len(params),2)
        self.assertEqual(result,"0aa5e893-ac14-4b0b-9025-f08d8f7f6ba8")

    def test_rejects_client_code_as_account_id(self):
        with self.assertRaises(ValueError):
            self.store.create("IND-TEST-1",self.digest,300)

    def test_rejects_non_sha256_digest(self):
        with self.assertRaises(ValueError):
            self.store.consume_and_enroll(self.uid,b"short")

    def test_rejects_unbounded_expiration(self):
        with self.assertRaises(ValueError):
            self.store.create(self.uid,self.digest,86400)


if __name__=="__main__":
    unittest.main()
