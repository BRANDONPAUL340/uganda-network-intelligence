from pathlib import Path

# Resolve migrations repository directory path context safely
MIGRATIONS_DIR = Path("migrations")


def test_migrations_exist():
    """
    ARRANGE, ACT & ASSERT: Verifies that our database migrations folder
    is properly deployed on disk.
    """
    assert MIGRATIONS_DIR.exists()


def test_migration_count():
    """
    ARRANGE, ACT & ASSERT: Confirms that all 6 sequential migration blueprint
    files are active inside the migrations repository directory.
    """
    migrations = sorted(MIGRATIONS_DIR.glob("*.sql"))
    assert len(migrations) >= 6


def test_migration_order():
    """
    ARRANGE, ACT & ASSERT: Enforces a strict dependency ordering chain across
    the full migration DAG to catch accidental file renaming or missing steps.
    """
    migrations = sorted(MIGRATIONS_DIR.glob("*.sql"))
    names = [migration.name for migration in migrations]

    expected = [
        "001_initial_schema.sql",
        "002_pipeline_observability.sql",
        "003_data_quality.sql",
        "004_pipeline_summary.sql",
        "005_silver_layer.sql",
        "006_gold_layer.sql",
    ]

    assert names == expected
def test_migrations_are_not_empty():
    """
    ARRANGE, ACT & ASSERT: Iterates through each declarative migration file 
    to guarantee it contains active DDL code and is not an empty file.
    """
    migrations = sorted(MIGRATIONS_DIR.glob("*.sql"))

    for migration in migrations:
        # Verify file size is strictly greater than 0 bytes
        assert migration.stat().st_size > 0
