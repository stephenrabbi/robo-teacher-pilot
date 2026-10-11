"""Disposable SQLite credential laboratory, not mounted or suitable for real pupils.

Uses an injected SQLite connection; no public routes or session tokens.
The caller must protect the connection and independently authorize provisioning.
"""
import hashlib
import hmac
import secrets
import sqlite3
import threading
from .provisioning_gate import ProvisioningDecision

class SyntheticDurableCredentialLab:
    def __init__(self, connection):
        if not isinstance(connection, sqlite3.Connection):
            raise ValueError("Explicit synthetic SQLite connection required")
        self.db=connection
        self.lock=threading.RLock()
        with self.lock, self.db:
            self.db.execute("""CREATE TABLE IF NOT EXISTS synthetic_credentials(
                school TEXT NOT NULL, learner TEXT NOT NULL, salt BLOB NOT NULL,
                digest BLOB NOT NULL, failures INTEGER NOT NULL DEFAULT 0,
                locked INTEGER NOT NULL DEFAULT 0, epoch INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (school,learner))""")
            self.db.execute("""CREATE TABLE IF NOT EXISTS synthetic_used_recovery(
                decision_ref TEXT PRIMARY KEY, school TEXT NOT NULL, learner TEXT NOT NULL)""")

    @staticmethod
    def _hash(password, salt):
        if not isinstance(password,str) or len(password)<16:
            raise ValueError("Synthetic credential must be at least 16 characters")
        return hashlib.scrypt(password.encode(),salt=salt,n=2**14,r=8,p=1,dklen=32)

    def activate(self, *, decision, password):
        if not isinstance(decision,ProvisioningDecision) or decision.allowed is not True:
            raise PermissionError("Authorization required")
        school,learner=decision.school_ref,decision.learner_ref
        if not isinstance(school,str) or not school or not isinstance(learner,str) or not learner:
            raise PermissionError("Invalid scope")
        salt=secrets.token_bytes(16)
        digest=self._hash(password,salt)
        with self.lock,self.db:
            try:
                self.db.execute("""INSERT INTO synthetic_credentials
                    (school,learner,salt,digest) VALUES (?,?,?,?)""",(school,learner,salt,digest))
            except sqlite3.IntegrityError as exc:
                raise PermissionError("Already provisioned") from exc

    def login(self, *, school_ref, learner_ref, password):
        with self.lock,self.db:
            row=self.db.execute("""SELECT salt,digest,failures,locked,epoch FROM synthetic_credentials
                WHERE school=? AND learner=?""",(school_ref,learner_ref)).fetchone()
            if row is None or row[3] or not isinstance(password,str):
                raise PermissionError("Invalid credentials")
            try:
                supplied=self._hash(password,row[0])
            except ValueError:
                supplied=b""
            if not hmac.compare_digest(supplied,row[1]):
                self.db.execute("""UPDATE synthetic_credentials SET failures=failures+1,
                    locked=CASE WHEN failures+1>=5 THEN 1 ELSE 0 END
                    WHERE school=? AND learner=?""",(school_ref,learner_ref))
                # Commit before raising so failed-attempt lockouts survive restarts.
                self.db.commit()
                raise PermissionError("Invalid credentials")
            self.db.execute("""UPDATE synthetic_credentials SET failures=0
                WHERE school=? AND learner=?""",(school_ref,learner_ref))
            return {"synthetic_school":school_ref,"synthetic_learner":learner_ref,"session_epoch":row[4]}

    def revoke_all(self, *, school_ref, learner_ref):
        with self.lock,self.db:
            result=self.db.execute("""UPDATE synthetic_credentials SET epoch=epoch+1
                WHERE school=? AND learner=? RETURNING epoch""",(school_ref,learner_ref)).fetchone()
            if result is None:
                raise PermissionError("Unknown account")
            return result[0]

    def verify_epoch(self, *, school_ref, learner_ref, epoch):
        with self.lock:
            row=self.db.execute("""SELECT epoch,locked FROM synthetic_credentials
                WHERE school=? AND learner=?""",(school_ref,learner_ref)).fetchone()
            if row is None or row[1] or type(epoch) is not int or row[0]!=epoch:
                raise PermissionError("Revoked or locked account")
            return True

    def recover(self, *, recovery_gate, approval, operator_proof, new_password, now=None):
        """Synthetic recovery replaces verifier and increments epoch atomically."""
        from .recovery_gate import SyntheticRecoveryGate
        if not isinstance(recovery_gate,SyntheticRecoveryGate):
            raise PermissionError("Recovery authority required")
        school,learner,decision_ref=recovery_gate.authorize(approval=approval,operator_proof=operator_proof,now=now)
        salt=secrets.token_bytes(16)
        digest=self._hash(new_password,salt)
        with self.lock,self.db:
            try:
                self.db.execute("INSERT INTO synthetic_used_recovery(decision_ref,school,learner) VALUES (?,?,?)",
                                (decision_ref,school,learner))
            except sqlite3.IntegrityError as exc:
                raise PermissionError("Recovery approval already redeemed") from exc
            row=self.db.execute("""UPDATE synthetic_credentials
                SET salt=?,digest=?,failures=0,locked=0,epoch=epoch+1
                WHERE school=? AND learner=? RETURNING epoch""",
                (salt,digest,school,learner)).fetchone()
            if row is None:
                raise PermissionError("Unknown account")
            return row[0]
