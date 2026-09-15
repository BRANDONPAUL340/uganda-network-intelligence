from src.quality.quarantine_metrics import get_quarantine_summary


def test_quarantine_summary_is_callable():
    """ARRANGE, ACT & ASSERT: Verifies the quarantine summary analysis function is fully callable."""
    assert callable(get_quarantine_summary)
