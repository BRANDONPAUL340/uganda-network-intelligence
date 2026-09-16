from src.monitoring.health import evaluate_pipeline_health, AlertSeverity


def test_health_evaluator_returns_valid_structure():
    """ARRANGE, ACT & ASSERT: Audits the health monitoring engine to ensure schema contract compliance [INDEX]."""
    report = evaluate_pipeline_health()
    
    assert isinstance(report, dict)
    assert "timestamp" in report
    assert "pipeline_name" in report
    assert "status" in report
    assert "severity" in report
    assert "checks" in report
    assert "alerts" in report
    assert report["severity"] in [AlertSeverity.INFO, AlertSeverity.WARNING, AlertSeverity.CRITICAL]
