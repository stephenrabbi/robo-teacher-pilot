"""Synthetic-only provisioning authorization; NEVER creates credentials or sessions.

Operator proof is a separately injected verifier, not a caller-provided boolean.
An in-memory audit sink is used only for disposable fixtures. No real identities.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from .enrollment_gate import SyntheticEnrollmentGate

@dataclass(frozen=True)
class ProvisioningDecision:
    learner_ref: str
    school_ref: str
    operator_ref: str
    allowed: bool

class SyntheticProvisioningGate:
    def __init__(self, *, enrollment_gate: SyntheticEnrollmentGate, verify_operator, audit_sink):
        if not isinstance(enrollment_gate, SyntheticEnrollmentGate):
            raise ValueError("Enrollment gate required")
        if not callable(verify_operator) or not callable(audit_sink):
            raise ValueError("Independent operator verifier and audit sink required")
        self.enrollment_gate=enrollment_gate
        self.verify_operator=verify_operator
        self.audit_sink=audit_sink

    def authorize(self, *, learner_ref, school_ref, school_decision, guardian_decision,
                  operator_proof, now=None):
        now=now or datetime.now(timezone.utc)
        allowed=False
        operator_ref="unverified"
        try:
            self.enrollment_gate.evaluate(learner_ref=learner_ref,school_ref=school_ref,
                school_decision=school_decision,guardian_decision=guardian_decision,now=now)
            identity=self.verify_operator(operator_proof)
            if not isinstance(identity,str) or not identity or identity in (
                school_decision.issuer_ref,guardian_decision.issuer_ref
            ):
                raise PermissionError("Operator not independently authorized")
            operator_ref=identity
            allowed=True
            return ProvisioningDecision(learner_ref,school_ref,operator_ref,True)
        finally:
            # Audit must succeed before authorization can return.
            self.audit_sink({"action":"synthetic_provisioning_authorization",
                "scope":"synthetic","allowed":allowed,"operator_ref":operator_ref,
                "occurred_at":now.isoformat()})
