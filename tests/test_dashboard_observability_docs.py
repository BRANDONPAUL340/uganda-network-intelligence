from pathlib import Path


def test_dashboard_observability_documentation():
    """ARRANGE, ACT & ASSERT: Guarantees that the dashboard observability manual exists and contains all mandatory sections [INDEX]."""
    path = Path("docs/dashboard_observability.md")

    assert path.exists()

    content = path.read_text(encoding="utf-8")

    assert "Dashboard Observability" in content
    assert "PostgreSQL" in content
    assert "Podman" in content
    assert "query" in content.lower()
