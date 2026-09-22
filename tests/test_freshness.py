from src.monitoring.freshness import check_measurement_freshness


def test_freshness_exists():
    """ARRANGE, ACT & ASSERT: Verifies that the freshness engine detects an ingestion watermark timestamp."""
    result = check_measurement_freshness()
    assert result is not None
