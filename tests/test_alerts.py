from src.monitoring.alerts import generate_alerts


def test_critical_alert_is_generated():
    """ARRANGE, ACT & ASSERT: Verifies that a CRITICAL token generates an actionable payload map [INDEX]."""
    report = {
        "checks": {
            "database": "HEALTHY",
            "latest_pipeline_run": "CRITICAL",
        }
    }
    alerts = generate_alerts(report)

    assert len(alerts) == 1
    assert alerts[0]["severity"] == "CRITICAL"
    assert alerts[0]["check"] == "latest_pipeline_run"


def test_healthy_report_has_no_alerts():
    """ARRANGE, ACT & ASSERT: Verifies that a pure HEALTHY status maps cleanly to an empty alerts array [INDEX]."""
    report = {
        "checks": {
            "database": "HEALTHY",
            "latest_pipeline_run": "HEALTHY",
        }
    }
    alerts = generate_alerts(report)
    assert alerts == []
