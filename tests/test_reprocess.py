from src.quality.reprocess import reprocess_quarantined_record


def test_reprocess_function_is_callable():
    """ARRANGE, ACT & ASSERT: Verifies the reprocessing driver engine is fully callable."""
    assert callable(reprocess_quarantined_record)
