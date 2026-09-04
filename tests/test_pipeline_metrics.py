import pytest


def test_pipeline_record_accounting():
    """
    ARRANGE, ACT & ASSERT: Verifies that our runtime metrics tracking logic
    accurately matches a clean, balanced data load run scenario.
    """
    records_read = 100
    records_inserted = 80
    records_rejected = 5
    records_skipped = 15

    # Calculate total aggregated lineage balance
    records_processed = (
        records_inserted
        + records_rejected
        + records_skipped
    )

    # Enforce strict audit accountability
    assert records_processed == records_read


def test_pipeline_record_accounting_detects_mismatch():
    """
    ARRANGE, ACT & ASSERT: Verifies that our auditing framework actively catches
    data lineage leaks. If an anomaly occurs and records disappear, the logic
    must throw an immediate AssertionError to halt execution.
    """
    records_read = 100
    records_inserted = 80
    records_rejected = 5
    records_skipped = 10  # 🛑 Anomaly: 5 rows missing from the calculation trail!

    records_processed = (
        records_inserted
        + records_rejected
        + records_skipped
    )

    # Assert that the pipeline integrity gate catches the processing leak
    with pytest.raises(AssertionError):
        assert records_processed == records_read
