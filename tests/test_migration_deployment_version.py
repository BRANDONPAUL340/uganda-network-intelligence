from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_deployment_version_migration_exists():
    """ARRANGE, ACT & ASSERT: Verifies the deployment version migration file exists on disk [INDEX]."""
    migrations_dir = PROJECT_ROOT / "database" / "migrations"
    matches = list(migrations_dir.glob("*deployment_version*.sql"))
    assert matches, "The deployment_version migration script file is missing from database/migrations."


def test_deployment_version_migration_is_additive():
    """ARRANGE, ACT & ASSERT: Guarantees the migration is strictly additive and includes IF NOT EXISTS guardrails [INDEX]."""
    migrations_dir = PROJECT_ROOT / "database" / "migrations"
    migration = next(migrations_dir.glob("*deployment_version*.sql"))
    content = migration.read_text(encoding="utf-8").upper()

    assert "ALTER TABLE PIPELINE_RUNS" in content, "Migration must target the pipeline_runs table."
    assert "ADD COLUMN" in content, "Migration must use an additive ADD COLUMN statement."
    assert "DEPLOYMENT_VERSION" in content, "Migration must declare the deployment_version column name."
    assert "IF NOT EXISTS" in content, "Migration must include IF NOT EXISTS logic to guarantee idempotency."
