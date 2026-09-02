import pytest

from src.ingestion.measurements import (
    create_source_record_id,
    validate_measurement,
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

    # Assert that the signatures are non-volatile and perfectly equal
    assert first == second
    assert first == "1_1_2026-09-02 08:00:00"


def test_missing_field_is_rejected():
    """
    ARRANGE, ACT & ASSERT: Verifies that your structural contract validation 
    shields successfully intercept incomplete source records. If a record lacks 
    required metric elements, the function must throw an immediate ValueError exception.
    """
    # This sample dictionary record misses vital metrics fields (traffic, latency, etc.)
    record = {
        "equipment_id": "1",
        "site_id": "1",
        "measured_at": "2026-09-02 08:00:00",
    }

    # Assert that the validation firewall actively catches the data-shape violation
    with pytest.raises(ValueError) as exc_info:
        validate_measurement(record)
        
    assert "Missing required field" in str(exc_info.value)
