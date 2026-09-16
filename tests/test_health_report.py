from src.monitoring.report import generate_health_report


def test_health_report_structure():
    """ARRANGE, ACT & ASSERT: Verifies the telemetry data structure contract matches framework rules [INDEX]."""
    report = generate_health_report()

    assert "overall_status" in report
    assert "checks" in report
    assert isinstance(report["checks"], dict)
