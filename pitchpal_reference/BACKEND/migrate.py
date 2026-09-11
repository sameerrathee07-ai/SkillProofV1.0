"""
Idempotent schema migration for the existing SQLite file.

Base.metadata.create_all() only creates tables that don't exist yet — it never
alters one that does. The Google sign-in work adds three columns to `users` and
makes `password_hash` nullable, so an already-created pitchpal.db needs this.

Safe to run repeatedly. Run once after pulling the Google auth change:

    py migrate.py
"""
import os
import sqlite3
import sys

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pitchpal.db")

if not DATABASE_URL.startswith("sqlite"):
    sys.exit("migrate.py only handles SQLite. For Postgres, use a real migration tool (Alembic).")

DB_PATH = DATABASE_URL.split("///")[-1]

if not os.path.exists(DB_PATH):
    print(f"No database at {DB_PATH} — nothing to migrate. It will be created on first run.")
    sys.exit(0)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("PRAGMA table_info(users)")
cols = {row[1]: row for row in cur.fetchall()}
if not cols:
    print("No `users` table yet — nothing to migrate.")
    conn.close()
    sys.exit(0)

# 1. Add the new nullable columns.
for name, ddl in (
    ("google_sub", "ALTER TABLE users ADD COLUMN google_sub VARCHAR"),
    ("name", "ALTER TABLE users ADD COLUMN name VARCHAR"),
    ("picture", "ALTER TABLE users ADD COLUMN picture VARCHAR"),
):
    if name in cols:
        print(f"  = users.{name} already present")
    else:
        cur.execute(ddl)
        print(f"  + added users.{name}")

cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_google_sub ON users (google_sub)")

# 2. Relax password_hash to nullable. SQLite can't ALTER a NOT NULL constraint,
#    so rebuild the table and copy the rows across.
cur.execute("PRAGMA table_info(users)")
pw = next((r for r in cur.fetchall() if r[1] == "password_hash"), None)
if pw and pw[3] == 1:  # notnull flag
    print("  ~ rebuilding users to make password_hash nullable")
    cur.executescript(
        """
        PRAGMA foreign_keys=OFF;
        BEGIN;
        CREATE TABLE users_new (
            id INTEGER NOT NULL PRIMARY KEY,
            email VARCHAR NOT NULL,
            password_hash VARCHAR,
            google_sub VARCHAR,
            name VARCHAR,
            picture VARCHAR,
            created_at DATETIME
        );
        INSERT INTO users_new (id, email, password_hash, google_sub, name, picture, created_at)
            SELECT id, email, password_hash, google_sub, name, picture, created_at FROM users;
        DROP TABLE users;
        ALTER TABLE users_new RENAME TO users;
        CREATE UNIQUE INDEX ix_users_email ON users (email);
        CREATE UNIQUE INDEX ix_users_google_sub ON users (google_sub);
        COMMIT;
        PRAGMA foreign_keys=ON;
        """
    )
else:
    print("  = users.password_hash already nullable")

conn.commit()
conn.close()
print("Migration complete.")
