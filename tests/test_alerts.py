from src.monitoring.alerts import create_alert
from src.monitoring.pipeline_alerts import check_pipeline_status
from src.monitoring.sla import create_sla_alert
from src.monitoring.watermark_alerts import check_watermark


def test_create_alert():
    """ARRANGE, ACT & ASSERT: Verifies the baseline alert object instantiates correctly."""
    alert = create_alert("test_alert", "SEV3", "Test message")
    assert alert.name == "test_alert"
    assert alert.severity == "SEV3"
    assert alert.triggered is True


def test_failed_pipeline_creates_alert():
    """ARRANGE, ACT & ASSERT: Catches failure flags and triggers an alert."""
    alert = check_pipeline_status("FAILED")
    assert alert is not None
    assert alert.name == "pipeline_failure"


def test_successful_pipeline_has_no_alert():
    """ARRANGE, ACT & ASSERT: Confirms that successful pipeline runs create no alerts."""
    alert = check_pipeline_status("SUCCESS")
    assert alert is None


def test_sla_breach_creates_alert():
    """ARRANGE, ACT & ASSERT: Confirms that breaching SLA limits triggers an alert."""
    alert = create_sla_alert(120, 60)
    assert alert is not None
    assert alert.name == "pipeline_sla_breach"


def test_sla_within_limit_has_no_alert():
    """ARRANGE, ACT & ASSERT: Confirms that runs finishing within limits create no alerts."""
    alert = create_sla_alert(30, 60)
    assert alert is None


def test_watermark_regression_creates_alert():
    """ARRANGE, ACT & ASSERT: Confirms that high-watermark regression triggers an alert."""
    alert = check_watermark(40, 45)
    assert alert is not None
    assert alert.name == "watermark_regression"


def test_watermark_progression_has_no_alert():
    """ARRANGE, ACT & ASSERT: Confirms that valid watermark forward progress creates no alerts."""
    alert = check_watermark(50, 45)
    assert alert is None
