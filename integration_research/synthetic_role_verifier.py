"""Test-only signed role assertions. NOT an institutional identity provider.

Issuer configuration and role allowlists must be supplied out of band.
No web routes, credential provisioning, or real school identities.
"""
import base64
import hashlib
import hmac
import json
import time

def _b64(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

def issue_synthetic_role(*, actor, role, secret, expires, issuer="synthetic-lab"):
    if not isinstance(secret,bytes) or len(secret)<32 or not actor or role not in ("operator","reviewer"):
        raise ValueError("Invalid fixture signing inputs")
    payload=json.dumps({"sub":actor,"role":role,"iss":issuer,"exp":int(expires)},
                       sort_keys=True,separators=(",",":")).encode()
    body=_b64(payload)
    signature=_b64(hmac.new(secret,body.encode(),hashlib.sha256).digest())
    return body+"."+signature

class SyntheticRoleVerifier:
    def __init__(self, *, secret, role, actors, issuer="synthetic-lab", clock=None):
        if not isinstance(secret,bytes) or len(secret)<32 or role not in ("operator","reviewer") or not actors:
            raise ValueError("Verifier requires secret, role and actor allowlist")
        self.secret=secret
        self.role=role
        self.actors=frozenset(actors)
        self.issuer=issuer
        self.clock=clock or time.time

    def __call__(self, proof):
        try:
            if not isinstance(proof,str) or len(proof)>4096:
                return None
            body,signature=proof.split(".")
            expected=_b64(hmac.new(self.secret,body.encode(),hashlib.sha256).digest())
            if not hmac.compare_digest(expected,signature):
                return None
            payload=json.loads(base64.urlsafe_b64decode(body+"="*((-len(body))%4)))
            if set(payload)!={"sub","role","iss","exp"}:
                return None
            if (payload["role"]!=self.role or payload["iss"]!=self.issuer
                or payload["sub"] not in self.actors or type(payload["exp"]) is not int
                or payload["exp"]<=self.clock()):
                return None
            return payload["sub"]
        except (ValueError,TypeError,KeyError,UnicodeError,OverflowError):
            return None
