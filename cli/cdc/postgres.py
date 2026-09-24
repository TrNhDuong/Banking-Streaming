from ..env import env
from ..process import run
from ._common import tables


def sql():
    u = env("DB_USER", "debezium")
    pw = env("DB_PASSWORD", "debezium_password")
    pub = env("POSTGRES_PUBLICATION_NAME", "banking_publication")
    db = env("DB_NAME", "banking")
    tbl = ", ".join(f'"{s}"."{t}"' for s, t in tables())
    return f"""
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{u}') THEN
    CREATE ROLE "{u}" LOGIN REPLICATION PASSWORD '{pw}';
  ELSE
    ALTER ROLE "{u}" LOGIN REPLICATION PASSWORD '{pw}';
  END IF;
END $$;
GRANT CONNECT ON DATABASE "{db}" TO "{u}";
GRANT USAGE ON SCHEMA public TO "{u}";
GRANT SELECT ON ALL TABLES IN SCHEMA public TO "{u}";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO "{u}";
DROP PUBLICATION IF EXISTS "{pub}";
CREATE PUBLICATION "{pub}" FOR TABLE {tbl};
"""


def setup():
    run(
        [
            "docker", "exec", "-i", "banking-postgres",
            "psql", "-v", "ON_ERROR_STOP=1",
            "-U", env("POSTGRES_ADMIN_USER", "bank_admin"),
            "-d", env("DB_NAME", "banking"),
        ],
        input_text=sql(),
    )


def verify():
    q = (
        "SHOW wal_level; "
        "SELECT pubname FROM pg_publication; "
        "SELECT slot_name,active FROM pg_replication_slots;"
    )
    run(
        [
            "docker", "exec", "-i", "banking-postgres",
            "psql",
            "-U", env("POSTGRES_ADMIN_USER", "bank_admin"),
            "-d", env("DB_NAME", "banking"),
        ],
        input_text=q,
    )
