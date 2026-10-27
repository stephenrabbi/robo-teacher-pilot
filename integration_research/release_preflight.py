"""Release preflight for the learner-identity integration branch.

Cannot certify real institutional approvals. Fails closed until verified inputs
exist; never reads or prints any secret or identifiable learner information.
"""
import os
import sys
from pathlib import Path

REQUIRED = (
    "ROBO_IDENTITY_PROVIDER_VERIFIED",
    "ROBO_INSTITUTIONAL_APPROVALS_VERIFIED",
    "ROBO_GUARDIAN_AUTHORIZATION_VERIFIED",
    "ROBO_PROTECTED_STAGING_VERIFIED",
    "ROBO_PRIVACY_SECURITY_SIGNOFF_VERIFIED",
    "ROBO_MANAGED_POSTGRES_VERIFIED",
    "ROBO_ROLLBACK_VERIFIED",
)

def assess(values):
    return [key for key in REQUIRED if values.get(key) != "true"]

if __name__ == "__main__":
    missing = assess(os.environ)
    if missing:
        print("BLOCKED: production learner-identity activation is not authorized.")
        for key in missing:
            print(" - Missing release evidence:", key)
        sys.exit(1)
    print("Configuration assertions present; independent evidence review STILL required.")
