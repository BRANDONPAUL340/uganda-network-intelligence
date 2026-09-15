from src.quality.reprocessing_metrics import get_reprocessing_summary


def test_reprocessing_summary_is_callable():
    """ARRANGE, ACT & ASSERT: Verifies the quarantine reprocessing metrics summary is fully callable."""
    assert callable(get_reprocessing_summary)
