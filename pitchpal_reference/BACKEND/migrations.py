"""
Additive schema migrations for databases that predate a column.

Base.metadata.create_all() creates missing *tables* and silently ignores
missing *columns*, so a model gains a field and every query against an
existing database starts failing with "no such column". This module closes
that gap for the additive case, which is all we have needed so far.

Deliberately narrow: it adds columns, and it never drops, renames or retypes
anything. Anything destructive belongs in a reviewed migration, not in a
startup hook that runs unattended.
"""

import logging

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

# table -> column -> DDL fragment used in ALTER TABLE ... ADD COLUMN.
# A NOT NULL column needs a DEFAULT, or the ALTER fails on any non-empty table.
ADDITIVE_COLUMNS = {
    "users": {
        "password_hash": "VARCHAR",                        # nullable: Google-only accounts
        "google_sub": "VARCHAR",
        "name": "VARCHAR",
        "picture": "VARCHAR",
        "pdf_downloads": "INTEGER NOT NULL DEFAULT 0",
    },
    "pitch_sessions": {
        "scores_json": "TEXT",
        "pitch_text": "TEXT",
        "current_step": "INTEGER DEFAULT 1",
    },
}


def ensure_schema(engine: Engine) -> list[str]:
    """Add any missing columns. Idempotent — safe to call on every boot.

    Returns the list of applied changes so startup can log what it did.
    """
    applied: list[str] = []
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    for table, columns in ADDITIVE_COLUMNS.items():
        if table not in existing_tables:
            continue  # create_all() will build it complete
        present = {col["name"] for col in inspector.get_columns(table)}
        for column, ddl in columns.items():
            if column in present:
                continue
            # Identifiers come from this module's own literals, never from a
            # request, so there is no injection surface here.
            with engine.begin() as conn:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))
            applied.append(f"{table}.{column}")
            logger.info("migration: added %s.%s", table, column)

    return applied
