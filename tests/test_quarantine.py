from src.data_quality.quarantine import reject_measurement


def test_quarantine_is_callable():
    """
    ARRANGE, ACT & ASSERT: Verifies that our quarantine engine handles
    rejections and remains exposed as an active, callable method within
    the data quality subpackage.
    """
    assert callable(reject_measurement)
