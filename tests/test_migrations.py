from pathlib import Path


def test_migrations_exist():
    """
    ARRANGE, ACT & ASSERT: Verifies that our database migrations folder
    is properly deployed on disk and contains our core migration scripts.
    """
    migrations_dir = Path("migrations")
    assert migrations_dir.exists()

    migrations = sorted(migrations_dir.glob("*.sql"))
    assert len(migrations) >= 3


def test_migrations_are_numbered():
    """
    ARRANGE, ACT & ASSERT: Confirms that our DDL migration scripts use our
    strict sequential prefix layout to preserve the dependency ordering chain.
    """
    migrations_dir = Path("migrations")
    migrations = sorted(migrations_dir.glob("*.sql"))

    names = [migration.name for migration in migrations]

    assert "001_initial_schema.sql" in names
    assert "002_pipeline_observability.sql" in names
    assert "003_pipeline_summary.sql" in names
