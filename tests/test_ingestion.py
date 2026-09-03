import pytest

from src.ingestion.measurements import (
    create_source_record_id,
)
from src.data_quality.measurements import (
    validate_record,
    get_validation_failure,
)


def test_source_record_id_is_deterministic():
    """
    ARRANGE, ACT & ASSERT: Verifies that the natural composite key generator 
    is mathematically deterministic. The exact same record dictionary data input 
    must yield an identical, predictable string key output signature every time.
    """
    record = {
        "equipment_id": "1",
        "site_id": "1",
        "measured_at": "2026-09-02 08:00:00",
    }

    first = create_source_record_id(record)
    second = create_source_record_id(record)

    assert first == second
    assert first == "1_1_2026-09-02 08:00:00"


def test_missing_field_is_rejected():
    """
    ARRANGE, ACT & ASSERT: Verifies that your structural contract validation 
    shields successfully intercept incomplete source records using our updated framework.
    """
    # This sample dictionary record misses vital metrics fields (traffic, latency, etc.)
    record = {
        "equipment_id": "1",
        "site_id": "1",
        "measured_at": "2026-09-02 08:00:00",
    }

    # Evaluate the row through the centralized validate_record chain
    checks = validate_record(record)
    reason = get_validation_failure(checks)

    # Assert that the validation firewall actively catches the data-shape violation
    assert reason is not None
    assert "Missing fields" in reason
