from pathlib import Path
from src.migrations import (
    MIGRATIONS_DIR,
    get_applied_migrations,
    get_migration_files,
)


def test_migrations_directory_exists():
    """ARRANGE, ACT & ASSERT: Verifies the migrations catalog directory is present on disk."""
    assert MIGRATIONS_DIR.exists()


def test_migration_files_exist():
    """ARRANGE, ACT & ASSERT: Verifies that at least 3 historical SQL scripts exist."""
    migration_files = get_migration_files()
    assert len(migration_files) >= 3


def test_migrations_are_sorted():
    """ARRANGE, ACT & ASSERT: Guarantees that script files follow strict alphanumeric order."""
    migration_files = get_migration_files()
    versions = [file.name.split("_", 1)[0] for file in migration_files]
    assert versions == sorted(versions)


def test_applied_migrations_are_available():
    """ARRANGE, ACT & ASSERT: Confirms the applied rows query yields a native Python set."""
    applied = get_applied_migrations()
    assert isinstance(applied, set)
