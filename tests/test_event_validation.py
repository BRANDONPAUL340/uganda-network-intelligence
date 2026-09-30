import pytest
from src.monitoring.event_contract import validate_event


@pytest.fixture
def baseline_valid_v1_envelope():
    """Generates a fully compliant version 1 event envelope dictionary blueprint [INDEX]."""
    return {
        "event_id": "evt_20260930_1a2b3c4d",
        "event_type": "QUALITY_CHECK_FAILED",
        "event_version": 1,
        "run_id": 151,
        "event_time": "2026-09-30T15:51:00Z",
        "producer": "quality_engine",
        "payload": {
            "check_name": "duplicate_check",
            "status": "FAIL",
            "failed_records": 27,
            "message": "Duplicate entries caught."
        }
    }


def test_13_unmapped_status_enum_value_is_flagged_with_descriptive_error(baseline_valid_v1_envelope):
    """Test 13: Asserts that status flags like 'BANANA' are caught and added to the error list [INDEX]."""
    baseline_valid_v1_envelope["payload"]["status"] = "BANANA"
    result = validate_event(baseline_valid_v1_envelope)
    
    assert result["valid"] is False
    assert any("Invalid status parameter value" in err for err in result["errors"])


def test_14_negative_failed_records_parameter_violates_business_validation_rules(baseline_valid_v1_envelope):
    """Test 14: Asserts that data type boundaries (e.g., negative failed_records) are flagged as rule violations [INDEX]."""
    baseline_valid_v1_envelope["payload"]["failed_records"] = -5
    result = validate_event(baseline_valid_v1_envelope)
    
    assert result["valid"] is False
    assert any("cannot be negative" in err for err in result["errors"])


def test_14_failed_status_with_zero_records_is_flagged_as_business_contradiction(baseline_valid_v1_envelope):
    """Test 14: Asserts that business logic conflicts (status='FAIL' with 0 records) are identified cleanly [INDEX]."""
    baseline_valid_v1_envelope["payload"]["failed_records"] = 0
    result = validate_event(baseline_valid_v1_envelope)
    
    assert result["valid"] is False
    assert any("requires a 'failed_records' metric threshold > 0" in err for err in result["errors"])
def test_26_valid_event_clears_ingestion_firewall_smoothly():
    """Test 26: Asserts that a compliant event contract clears validation and inserts into PostgreSQL cleanly [INDEX]."""
    from src.monitoring.event_store import emit_pipeline_event
    from src.database import engine
    from sqlalchemy import text
    
    # Clean table state before starting the test pass
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE pipeline_event_store RESTART IDENTITY CASCADE;"))
        
    try:
        evt_id = emit_pipeline_event(
            event_type="QUALITY_CHECK_FAILED",
            run_id=151,
            producer="quality_engine",
            event_version=1,
            payload={
                "check_name": "duplicate_check",
                "status": "FAIL",
                "failed_records": 10,
                "message": "Duplicate measurements detected inside streaming loops."
            }
        )
        assert isinstance(evt_id, str)
    except Exception as exc:
        pytest.fail(f"Compliant event payload unexpectedly breached the upstream ingestion firewall: {exc}")


def test_invalid_event_payload_is_rejected_and_never_enters_database_store():
    """Test 24 & 25: Asserts that bad data is rejected upstream, leaving the database table untouched [INDEX]."""
    from src.monitoring.event_store import emit_pipeline_event
    from src.database import engine
    from sqlalchemy import text
    
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE pipeline_event_store RESTART IDENTITY CASCADE;"))
        
    # Attempt to ingest a payload that breaks business validation parameters [INDEX]
    with pytest.raises(EventContractValidationError):
        emit_pipeline_event(
            event_type="QUALITY_CHECK_FAILED",
            run_id=151,
            producer="quality_engine",
            event_version=1,
            payload={
                "check_name": "null_site_id",
                "status": "FAIL",
                "failed_records": 0,  # Fails business validation (status 'FAIL' requires records > 0) [INDEX]
                "message": "Contradictory state metadata test"
            }
        )
        
    # Verify that the rejected record was never written to the table on disk [INDEX]
    with engine.connect() as conn:
        stored_rows_count = conn.execute(text("SELECT COUNT(*) FROM pipeline_event_store;")).scalar()
        assert stored_rows_count == 0
