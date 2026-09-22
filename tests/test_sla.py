from src.monitoring.sla import evaluate_pipeline_sla, evaluate_freshness


def test_pipeline_sla_passes():
    """ARRANGE, ACT & ASSERT: Verifies a fast runtime marks as PASS."""
    assert evaluate_pipeline_sla(30) == "PASS"


def test_pipeline_sla_passes_at_boundary():
    """ARRANGE, ACT & ASSERT: Verifies a boundary match marks as PASS."""
    assert evaluate_pipeline_sla(60) == "PASS"


def test_pipeline_sla_breaches():
    """ARRANGE, ACT & ASSERT: Verifies long execution marks as BREACH."""
    assert evaluate_pipeline_sla(61) == "BREACH"


def test_pipeline_sla_unknown():
    """ARRANGE, ACT & ASSERT: Verifies missing values mark as UNKNOWN."""
    assert evaluate_pipeline_sla(None) == "UNKNOWN"


def test_freshness_passes():
    """ARRANGE, ACT & ASSERT: Verifies zero lag marks as PASS."""
    assert evaluate_freshness(0) == "PASS"


def test_freshness_passes_at_boundary():
    """ARRANGE, ACT & ASSERT: Verifies boundary lag marks as PASS."""
    assert evaluate_freshness(1) == "PASS"


def test_freshness_breaches():
    """ARRANGE, ACT & ASSERT: Verifies old data lag marks as BREACH."""
    assert evaluate_freshness(2) == "BREACH"


def test_freshness_unknown():
    """ARRANGE, ACT & ASSERT: Verifies missing values mark as UNKNOWN."""
    assert evaluate_freshness(None) == "UNKNOWN"

from src.monitoring.sla import check_sla


def test_sla_pass():
    """ARRANGE, ACT & ASSERT: Asserts true when actual duration falls well under the SLA ceiling [1]."""
    assert check_sla(20, 60) is True


def test_sla_fail():
    """ARRANGE, ACT & ASSERT: Asserts false when actual duration breaches the SLA performance ceiling [1]."""
    assert check_sla(120, 60) is False

