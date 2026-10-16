"""Offline synthetic provider assertions. Not connected to real school identity systems.

The shared key represents a configured trusted provider, never a browser secret.
An actual deployment requires provider authentication, key rotation, approval
record retention and a transactional replay database.
"""
import base64
import hashlib
import hmac
import json
import time
from .approval_evidence import VerifiedDecision

def _enc(value):
    return base64.urlsafe_b64encode(value).decode().rstrip("=")

def _dec(value):
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))

class SignedApprovalVerifier:
    def __init__(self, *, provider_id, secret, clock=None):
        if not isinstance(provider_id,str) or not provider_id.strip():
            raise ValueError("Trusted provider identifier required")
        if not isinstance(secret,bytes) or len(secret)<32:
            raise ValueError("Strong provider key required")
        self.provider_id=provider_id
        self._secret=secret
        self._clock=clock or time.time

    def verify(self, assertion):
        if not isinstance(assertion,str) or len(assertion)>8192 or assertion.count(".")!=1:
            raise PermissionError("Invalid provider assertion")
        try:
            payload_b64, mac_b64=assertion.split(".")
            if not payload_b64 or not mac_b64:
                raise ValueError("Empty assertion")
            signature=_dec(mac_b64)
            expected=hmac.new(self._secret,payload_b64.encode("ascii"),hashlib.sha256).digest()
            if not hmac.compare_digest(signature,expected):
                raise PermissionError("Untrusted provider assertion")
            values=json.loads(_dec(payload_b64))
            expected_keys={"issuer","decision_id","subject","school","reviewer_id","kind","approved","issued_at","expires_at"}
            if not isinstance(values,dict) or set(values)!=expected_keys:
                raise PermissionError("Invalid approval claims")
            if values["issuer"]!=self.provider_id or values["kind"] not in ("enrollment","recovery") or values["approved"] is not True:
                raise PermissionError("Approval denied or wrong provider")
            if any(not isinstance(values[k],str) or not values[k].strip() or len(values[k])>128 for k in ("decision_id","subject","school","reviewer_id")):
                raise PermissionError("Invalid approval scope")
            iat,exp=values["issued_at"],values["expires_at"]
            now=int(self._clock())
            if type(iat) is not int or type(exp) is not int or not iat<=now<exp or not 1<=exp-iat<=600:
                raise PermissionError("Expired or future provider approval")
            return VerifiedDecision(values["decision_id"],values["subject"],values["school"],values["reviewer_id"],values["kind"],True)
        except (ValueError,TypeError,UnicodeError,KeyError,OverflowError) as exc:
            raise PermissionError("Invalid provider assertion") from exc

def sign_synthetic_approval(values, *, secret):
    """Test fixture only; never expose an assertion issuer in public routes."""
    body=_enc(json.dumps(values,sort_keys=True,separators=(",",":")).encode())
    return body+"."+_enc(hmac.new(secret,body.encode(),hashlib.sha256).digest())
