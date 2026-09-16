from pathlib import Path


def test_dashboard_documentation_exists():
    """ARRANGE, ACT & ASSERT: Guarantees that the dashboard architecture guide exists and contains mandatory topics [INDEX]."""
    path = Path("docs/dashboard.md")

    assert path.exists()

    content = path.read_text(encoding="utf-8")

    assert "Streamlit" in content
    assert "PostgreSQL" in content
    assert "Operational KPIs" in content
    assert "Network Site Performance" in content
