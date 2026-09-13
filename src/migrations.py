import logging
from pathlib import Path
from sqlalchemy import text
from src.database import engine

# Instantiate localized logging context handle wrapper
logger = logging.getLogger(__name__)

# Resolve path points regardless of execution context origins
MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "database" / "migrations"


def get_migration_files():
    """Reads the migrations catalog and returns files sorted sequentially."""
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def ensure_migration_table():
    """Guarantees the structural existence of the schema version tracking table."""
    query = text(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(50) PRIMARY KEY,
            description VARCHAR(255) NOT NULL,
            applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    with engine.begin() as connection:
        connection.execute(query)


def get_applied_migrations():
    """Extracts all previously executed migration version strings from the database."""
    query = text(
        """
        SELECT version
        FROM schema_migrations
        ORDER BY version;
    """
    )
    with engine.connect() as connection:
        return {row[0] for row in connection.execute(query).fetchall()}


def apply_migration(migration_file):
    """Executes a single SQL migration file inside an atomic database transaction."""
    version = migration_file.name.split("_", 1)[0]
    description = migration_file.stem.split("_", 1)[1].replace("_", " ")

    sql = migration_file.read_text(encoding="utf-8")

    with engine.begin() as connection:
        # Execute raw database DDL alterations
        connection.execute(text(sql))

        # Log completion state inside the exact same active transaction context
        connection.execute(
            text(
                """
                INSERT INTO schema_migrations (version, description)
                VALUES (:version, :description)
                ON CONFLICT (version) DO NOTHING;
                """
            ),
            {
                "version": version,
                "description": description,
            },
        )


def run_migrations():
    """Scans the repository, compares files with history, and applies changes sequentially."""
    ensure_migration_table()

    applied = get_applied_migrations()
    migration_files = get_migration_files()

    for migration_file in migration_files:
        version = migration_file.name.split("_", 1)[0]

        if version in applied:
            logger.info("Migration %s already applied", version)
            continue

        logger.info("Applying migration %s", migration_file.name)
        apply_migration(migration_file)
        logger.info("Migration %s applied successfully", version)


# 🔑 Command-line entry point execution trigger gate
if __name__ == "__main__":
    # Boot a minimal log configuration for direct script calls
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    run_migrations()
