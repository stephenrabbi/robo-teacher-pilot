"""Disposable-only PostgreSQL role separation and interrupted-transaction drill."""
import os
from urllib.parse import urlparse
import psycopg
from psycopg import sql
from psycopg.errors import InsufficientPrivilege

DSN=os.environ.get("ROBO_SYNTHETIC_PG_DSN","")
u=urlparse(DSN)
if u.hostname not in ("localhost","127.0.0.1") or u.path!="/synthetic_progress":
    raise SystemExit("Refusing to run outside local disposable synthetic_progress")

with psycopg.connect(DSN,autocommit=True) as admin:
    admin.execute("CREATE ROLE rt_ci_runtime LOGIN PASSWORD 'temporary-runtime-only'")
    admin.execute("REVOKE ALL ON SCHEMA rt_synthetic FROM PUBLIC")
    admin.execute("GRANT USAGE ON SCHEMA rt_synthetic TO rt_ci_runtime")
    admin.execute("GRANT SELECT,INSERT ON rt_synthetic.events TO rt_ci_runtime")
    admin.execute("GRANT SELECT ON rt_synthetic.enrollments TO rt_ci_runtime")
    admin.execute("REVOKE CREATE ON SCHEMA rt_synthetic FROM rt_ci_runtime")

runtime_dsn="postgresql://rt_ci_runtime:temporary-runtime-only@localhost:5432/synthetic_progress"
try:
    with psycopg.connect(runtime_dsn) as runtime:
        assert runtime.execute("SELECT count(*) FROM rt_synthetic.enrollments").fetchone()[0] == 1
        for command in (
            "CREATE TABLE rt_synthetic.unapproved_change (id integer)",
            "UPDATE rt_synthetic.enrollments SET session_epoch=99",
            "DROP TABLE rt_synthetic.events",
        ):
            try:
                runtime.execute(command)
            except InsufficientPrivilege:
                runtime.rollback()
            else:
                raise AssertionError("Runtime role unexpectedly allowed: "+command)

    # Explicitly roll back an unacknowledged insert by closing the connection.
    pending=psycopg.connect(DSN)
    pending.execute("""INSERT INTO rt_synthetic.events
        (school,subject,event_id,event_type,class_level,topic_key,correct_count,total_count,occurred_at)
        VALUES ('school','acknowledged','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
        'practice_completed','JSS2','fractions',1,2,now())""")
    pending.close()
    with psycopg.connect(DSN) as check:
        assert check.execute("SELECT count(*) FROM rt_synthetic.events").fetchone()[0]==1
        assert check.execute("""SELECT session_epoch FROM rt_synthetic.enrollments
            WHERE school='school' AND subject='acknowledged'""").fetchone()[0]==2
finally:
    with psycopg.connect(DSN,autocommit=True) as admin:
        admin.execute("DROP OWNED BY rt_ci_runtime")
        admin.execute("DROP ROLE rt_ci_runtime")
print("Runtime role restrictions and uncommitted-write rollback verified.")
