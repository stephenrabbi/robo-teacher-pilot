"""Synthetic-only in-memory credential activation and login laboratory.

No routes, persistence or production session tokens. Provisioning decisions must
come from the independent gate; this model does not verify real people.
"""
import hashlib
import hmac
import secrets
from dataclasses import dataclass

@dataclass
class _Account:
    salt: bytes
    digest: bytes
    failures: int = 0
    locked: bool = False
    epoch: int = 0

class SyntheticCredentialLab:
    def __init__(self):
        self._accounts = {}

    @staticmethod
    def _hash(password, salt):
        if not isinstance(password, str) or len(password) < 16:
            raise ValueError("Synthetic credential must be at least 16 characters")
        return hashlib.scrypt(password.encode("utf-8"), salt=salt,
                              n=2**14, r=8, p=1, dklen=32)

    def activate(self, *, decision, password):
        from .provisioning_gate import ProvisioningDecision
        if not isinstance(decision, ProvisioningDecision) or decision.allowed is not True:
            raise PermissionError("Independent provisioning authorization required")
        scope=(decision.school_ref, decision.learner_ref)
        if not all(isinstance(x,str) and x for x in scope):
            raise PermissionError("Invalid synthetic scope")
        if scope in self._accounts:
            raise PermissionError("Account already provisioned")
        salt=secrets.token_bytes(16)
        digest=self._hash(password,salt)
        self._accounts[scope]=_Account(salt,digest)

    def login(self, *, school_ref, learner_ref, password):
        scope=(school_ref,learner_ref)
        account=self._accounts.get(scope)
        if account is None or account.locked or not isinstance(password,str):
            raise PermissionError("Invalid credentials")
        try:
            guess=self._hash(password,account.salt)
        except ValueError:
            guess=b""
        if not hmac.compare_digest(guess, account.digest):
            account.failures+=1
            if account.failures>=5:
                account.locked=True
            raise PermissionError("Invalid credentials")
        account.failures=0
        return {"synthetic_school":school_ref,"synthetic_learner":learner_ref,
                "session_epoch":account.epoch}

    def revoke_all(self, *, school_ref, learner_ref):
        account=self._accounts.get((school_ref,learner_ref))
        if account is None:
            raise PermissionError("Unknown account")
        account.epoch+=1
        return account.epoch
