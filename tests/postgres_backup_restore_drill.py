"""CI-only destructive backup/restore drill for disposable local PostgreSQL.

Never pass a production DSN. Creates and drops only rt_synthetic in CI.
"""
import os, pathlib, subprocess, tempfile, uuid
from urllib.parse import urlparse
import psycopg

dsn=os.environ.get("ROBO_SYNTHETIC_PG_DSN","")
parsed=urlparse(dsn)
if parsed.hostname not in ("localhost","127.0.0.1") or parsed.path!="/synthetic_progress":
    raise SystemExit("Refusing backup/restore outside disposable local synthetic_progress database")
migration=pathlib.Path(__file__).resolve().parents[1]/"progress_store/postgres/0001_synthetic_schema.sql"
with psycopg.connect(dsn) as db:
    with db.transaction():
        db.execute("DROP SCHEMA IF EXISTS rt_synthetic CASCADE")
    db.execute(migration.read_text())
    event_id=uuid.uuid4()
    with db.transaction():
        db.execute("""INSERT INTO rt_synthetic.enrollments
          (school,subject,reviewer_id,approved_at,session_epoch)
          VALUES ('school','acknowledged','reviewer',1000,2)""")
        db.execute("""INSERT INTO rt_synthetic.events
          (school,subject,event_id,event_type,class_level,topic_key,correct_count,total_count,occurred_at)
          VALUES ('school','acknowledged',%s,'practice_completed','JSS2','fractions',4,5,
          '2026-10-11T12:00:00+00:00')""",(event_id,))
with tempfile.TemporaryDirectory() as temp:
    archive=pathlib.Path(temp)/"synthetic.dump"
    with archive.open("wb") as out:
        subprocess.run(["pg_dump","--format=custom","--schema=rt_synthetic",dsn],stdout=out,check=True)
    if archive.stat().st_size==0:
        raise AssertionError("Backup archive empty")
    with psycopg.connect(dsn) as db:
        db.execute("DROP SCHEMA rt_synthetic CASCADE")
    subprocess.run(["pg_restore","--no-owner","--no-privileges","--dbname",dsn,str(archive)],check=True)
    with psycopg.connect(dsn) as restored:
        rows=restored.execute("""SELECT event_id,correct_count,total_count
            FROM rt_synthetic.events WHERE school='school' AND subject='acknowledged'""").fetchall()
        epoch=restored.execute("""SELECT session_epoch FROM rt_synthetic.enrollments
            WHERE school='school' AND subject='acknowledged'""").fetchone()
        assert rows==[(event_id,4,5)],"Acknowledged event lost or changed during restore"
        assert epoch==(2,),"Revocation state lost during restore"
        assert restored.execute("SELECT count(*) FROM rt_synthetic.events").fetchone()[0]==1
        restored.execute("DROP SCHEMA rt_synthetic CASCADE")
print("Disposable PostgreSQL backup and restore verified (event + revocation epoch).")
