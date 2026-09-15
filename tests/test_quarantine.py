from src.quality.quarantine import quarantine_invalid_records


def test_quarantine_function_is_callable():
    """ARRANGE, ACT & ASSERT: Verifies the quarantine engine exists as a callable function."""
    assert callable(quarantine_invalid_records)
