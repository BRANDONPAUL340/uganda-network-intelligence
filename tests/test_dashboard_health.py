from src.dashboard.health import (
    check_dashboard_database,
    get_dashboard_health,
)


def test_dashboard_database_health():
    """ARRANGE, ACT & ASSERT: Verifies that the database check returns a valid status string [INDEX]."""
    result = check_dashboard_database()

    assert result["status"] in {
        "HEALTHY",
        "WARNING",
        "CRITICAL",
    }


def test_dashboard_health_structure():
    """ARRANGE, ACT & ASSERT: Verifies the structural schema contract of the dashboard payload map [INDEX]."""
    result = get_dashboard_health()

    assert "application" in result
    assert "database" in result
