"""Synthetic-only PostgreSQL activation adapter; NOT connected to live services.

Requires a separately authenticated, scope-bound verifier and an externally
managed PostgreSQL connection. No credentials, sessions or real consent.
"""
import hashlib

class SyntheticPostgresActivation:
    def __init__(self, connection_factory, verify_decisions):
        if not callable(connection_factory) or not callable(verify_decisions):
            raise ValueError("Independent verifier and connection factory required")
        self.connect=connection_factory
        self.verify=verify_decisions

    def activate(self, *, school, learner, approval_proof):
        if not all(isinstance(x,str) and x for x in (school,learner,approval_proof)):
            raise PermissionError("Invalid activation scope")
        # Check before transaction; this verifier must validate authentic,
        # institutionally granted decisions. It is a deliberate release blocker.
        if self.verify(approval_proof,school,learner) is not True:
            raise PermissionError("Unverified authorization")
        fingerprint=hashlib.sha256(approval_proof.encode("utf-8")).hexdigest()
        connection=self.connect()
        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """INSERT INTO synthetic_identity_lab.approval_redemptions
                           (approval_fingerprint,school_ref,learner_ref)
                           VALUES (%s,%s,%s)""",(fingerprint,school,learner))
                    cursor.execute(
                        """INSERT INTO synthetic_identity_lab.learner_activations
                           (school_ref,learner_ref,approval_fingerprint)
                           VALUES (%s,%s,%s)""",(school,learner,fingerprint))
        finally:
            connection.close()
        return True
