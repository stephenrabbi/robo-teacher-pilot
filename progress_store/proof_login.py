"""Isolated synthetic proof-of-possession login (not exposed through HTTP).

Enrollment alone is insufficient to log in. A credential must be provisioned via
a trusted, separate channel. Only its salted scrypt verifier is stored. Real
minors require an approved guardian/school credential policy, throttling and
session revocation before release.
"""
import hashlib
import hmac
import secrets
import sqlite3
import time
from .session_auth import issue_test_session

def create_login_schema(db):
    db.execute("""CREATE TABLE IF NOT EXISTS synthetic_login_credentials (
        school TEXT NOT NULL, subject TEXT NOT NULL,
        salt BLOB NOT NULL, verifier BLOB NOT NULL,
        PRIMARY KEY(school,subject))""")
    db.execute("""CREATE TABLE IF NOT EXISTS synthetic_login_attempts (
        school TEXT NOT NULL, subject TEXT NOT NULL,
        failures INTEGER NOT NULL DEFAULT 0, locked_until INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY(school,subject))""")
    db.commit()

def _derive(password, salt):
    if not isinstance(password,str) or len(password)<16 or len(password)>256:
        raise PermissionError("Invalid login proof")
    return hashlib.scrypt(password.encode(),salt=salt,n=2**14,r=8,p=1,dklen=32)

class SyntheticProofLogin:
    def __init__(self,db,*,signing_key,clock=None):
        if not isinstance(signing_key,bytes) or len(signing_key)<32:
            raise ValueError("Server-held session signing key required")
        self.db=db
        self.signing_key=signing_key
        self.clock=clock or time.time

    def provision(self,*,school,subject,credential,authorized_operator=False):
        """Trusted synthetic test setup only. Never map this to a public route."""
        if authorized_operator is not True:
            raise PermissionError("Trusted provisioning required")
        salt=secrets.token_bytes(16)
        verifier=_derive(credential,salt)
        try:
            self.db.execute("BEGIN IMMEDIATE")
            enrolled=self.db.execute("SELECT 1 FROM synthetic_enrollments WHERE school=? AND subject=?",
                                     (school,subject)).fetchone()
            if not enrolled:
                raise PermissionError("Approved enrollment required")
            self.db.execute("INSERT INTO synthetic_login_credentials VALUES (?,?,?,?)",
                            (school,subject,salt,verifier))
            self.db.commit()
        except sqlite3.IntegrityError as exc:
            self.db.rollback()
            raise PermissionError("Credential already provisioned") from exc
        except Exception:
            self.db.rollback()
            raise

    def login(self,*,school,subject,credential):
        now=int(self.clock())
        try:
            self.db.execute("BEGIN IMMEDIATE")
            state=self.db.execute("SELECT failures,locked_until FROM synthetic_login_attempts WHERE school=? AND subject=?",
                                  (school,subject)).fetchone()
            if state and now<state[1]:
                raise PermissionError("Invalid credentials")
            if state and state[1] and now>=state[1]:
                self.db.execute("DELETE FROM synthetic_login_attempts WHERE school=? AND subject=?",(school,subject))
            row=self.db.execute("""SELECT c.salt,c.verifier,e.session_epoch FROM synthetic_login_credentials c
                JOIN synthetic_enrollments e ON e.school=c.school AND e.subject=c.subject
                WHERE c.school=? AND c.subject=?""",(school,subject)).fetchone()
            valid=False
            if row:
                try:
                    valid=hmac.compare_digest(_derive(credential,row[0]),row[1])
                except (PermissionError,ValueError,TypeError):
                    valid=False
            if not valid:
                self.db.execute("""INSERT INTO synthetic_login_attempts VALUES (?,?,1,0)
                    ON CONFLICT(school,subject) DO UPDATE SET failures=failures+1""",(school,subject))
                count=self.db.execute("SELECT failures FROM synthetic_login_attempts WHERE school=? AND subject=?",
                                      (school,subject)).fetchone()[0]
                if count>=5:
                    self.db.execute("UPDATE synthetic_login_attempts SET locked_until=? WHERE school=? AND subject=?",
                                    (now+900,school,subject))
                self.db.commit()
                raise PermissionError("Invalid credentials")
            self.db.execute("DELETE FROM synthetic_login_attempts WHERE school=? AND subject=?",(school,subject))
            token=issue_test_session(subject=subject,school=school,secret=self.signing_key,
                                     now=now,session_epoch=row[2])
            self.db.commit()
            return token
        except Exception:
            if self.db.in_transaction:
                self.db.rollback()
            raise
