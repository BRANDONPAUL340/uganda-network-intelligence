from pathlib import Path

# Anchors path routing explicitly to your workspace root directory context [INDEX]
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_required_release_files_exist():
    """ARRANGE, ACT & ASSERT: Guarantees all essential production deployment blueprints exist [INDEX]."""
    required_files = [
        "README.md",
        "requirements.txt",
        "Containerfile",
        "docker-compose.yml",
        ".github/workflows/ci.yml",
    ]

    for file_name in required_files:
        assert (PROJECT_ROOT / file_name).exists(), f"Mandatory deployment file '{file_name}' is missing from the root repository."


def test_dashboard_application_exists():
    """ARRANGE, ACT & ASSERT: Guarantees that the visual presentation tier entrypoint file is active on disk [INDEX]."""
    assert (PROJECT_ROOT / "src/dashboard/app.py").exists()


def test_database_schema_exists():
    """ARRANGE, ACT & ASSERT: Guarantees that the baseline database schema fallback backup DDL is active [INDEX]."""
    assert (PROJECT_ROOT / "database/schema.sql").exists()
