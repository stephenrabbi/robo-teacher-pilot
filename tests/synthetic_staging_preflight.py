"""Fail-closed source-level preflight for synthetic-only identity staging.

This deliberately cannot certify network access controls, identity providers,
or child-data handling. No deployment is initiated by this script.
"""
from pathlib import Path
import ast

ROOT=Path(__file__).resolve().parents[1]
PROTECTED=("main.py","v25_app.py")
FORBIDDEN=("integration_research.smoke_api","integration_research.durable_credential_lab",
           "integration_research.recovery_gate","integration_research.provisioning_gate",
           "integration_research.synthetic_role_verifier","integration_research.role_replay_guard")
for filename in PROTECTED:
    text=(ROOT/filename).read_text(encoding="utf-8")
    tree=ast.parse(text,filename=filename)
    imports=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node,ast.ImportFrom) and node.module:
            imports.append(node.module)
    prohibited=[name for name in imports if any(
        name==target or name.startswith(target+".") for target in FORBIDDEN)]
    if prohibited:
        raise SystemExit(f"FAIL: {filename} imports synthetic identity modules: {prohibited}")

from integration_research.smoke_api import build_synthetic_identity_smoke_app
try:
    build_synthetic_identity_smoke_app()
except RuntimeError:
    pass
else:
    raise SystemExit("FAIL: synthetic identity smoke app enabled by default")
app=build_synthetic_identity_smoke_app(enabled=True)
paths={route.path for route in app.routes}
assert "/internal/synthetic-identity/health" in paths
assert not any("/learner" in path or "/enroll" in path or "/recovery" in path
               or "/login" in path for path in paths)
print("PASS: no synthetic identity imports in live entries; smoke app has no sensitive routes")
