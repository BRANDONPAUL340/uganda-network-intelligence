from pathlib import Path


def test_health_monitoring_documentation_exists():
    """ARRANGE, ACT & ASSERT: Guarantees that the health monitoring blueprint file exists and contains all mandatory sections [INDEX]."""
    path = Path("docs/pipeline_health_monitoring.md")

    assert path.exists()

    content = path.read_text(encoding="utf-8")

    required_terms = [
        "HEALTHY",
        "WARNING",
        "CRITICAL",
        "UNKNOWN",
        "Pipeline Checks",
        "Database Checks",
        "Alert Severity",
    ]

    for term in required_terms:
        assert term in content, f"Mandatory operational term '{term}' is missing from health documentation."
