import unittest
from integration_research.postgres_atomic_activation import SyntheticPostgresActivation

class FakeConnection:
    def __init__(self, fail_second=False):
        self.statements=[]
        self.closed=False
        self.committed=False
        self.rolled_back=False
        self.fail_second=fail_second
    def __enter__(self): return self
    def __exit__(self,typ,val,tb):
        self.rolled_back=typ is not None
        self.committed=typ is None
        return False
    def cursor(self): return self
    def execute(self,sql,params):
        if self.fail_second and len(self.statements)==1:
            raise RuntimeError("synthetic account insert failure")
        self.statements.append((sql,params))
    def close(self): self.closed=True

class AdapterTests(unittest.TestCase):
    def test_two_inserts_one_transaction_and_close(self):
        conn=FakeConnection()
        adapter=SyntheticPostgresActivation(lambda:conn,
            lambda proof,school,learner: proof=="fixture" and school=="school-A" and learner=="learner-A")
        self.assertTrue(adapter.activate(school="school-A",learner="learner-A",approval_proof="fixture"))
        self.assertEqual(len(conn.statements),2)
        self.assertTrue(conn.committed)
        self.assertTrue(conn.closed)
        self.assertEqual(conn.statements[0][1][1:],("school-A","learner-A"))
        self.assertEqual(conn.statements[1][1][:2],("school-A","learner-A"))
        self.assertEqual(conn.statements[0][1][0],conn.statements[1][1][2])
    def test_failed_account_insert_rolls_back(self):
        conn=FakeConnection(fail_second=True)
        adapter=SyntheticPostgresActivation(lambda:conn,lambda *args:True)
        with self.assertRaises(RuntimeError):
            adapter.activate(school="school-A",learner="learner-A",approval_proof="fixture")
        self.assertTrue(conn.rolled_back)
        self.assertFalse(conn.committed)
        self.assertTrue(conn.closed)
    def test_forged_proof_does_not_connect(self):
        def cannot_connect(): raise AssertionError("Unauthorized request opened connection")
        adapter=SyntheticPostgresActivation(cannot_connect,lambda *args:False)
        with self.assertRaises(PermissionError):
            adapter.activate(school="school-A",learner="learner-A",approval_proof="forged")
if __name__=="__main__":
    unittest.main()
