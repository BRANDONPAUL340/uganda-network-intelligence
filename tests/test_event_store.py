import pytest
import json
from sqlalchemy import text
from src.database import engine
from src.monitoring.event_store import (
    emit_pipeline_event,
    publish_quality_event,
    consume_event_store_stream
)

@pytest.fixture(autouse=True)
def clean_event_and_processing_ledgers():
    """Resets the event store, processing matrix, and pipeline incident tables before each test run loop pass [1]."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE pipeline_event_store RESTART IDENTITY CASCADE;"))
        conn.execute(text("TRUNCATE TABLE event_processing RESTART IDENTITY CASCADE;"))
        conn.execute(text("TRUNCATE TABLE pipeline_incidents RESTART IDENTITY CASCADE;"))
    yield

def test_27_producer_creates_valid_event_upon_quality_failure():
    """Test 27: Verifies that a failed check produces a valid contract event on disk [1]."""
    mock_result = {
        "check_name": "null_site_id",
        "status": "FAIL",
        "failed_records": 15,
        "check_value": 1.2,
        "message": "Missing mandatory site context fields."
    }
    evt_id = publish_quality_event(run_id=161, result=mock_result)
    assert evt_id is not None
    
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT event_type, run_id, producer, payload FROM pipeline_event_store WHERE event_id = :evt_id;"),
            {"evt_id": evt_id}
        ).fetchone()
        assert row.event_type == "QUALITY_CHECK_FAILED"
        assert row.run_id == 161
        assert row.producer == "quality_engine"

def test_28_consumer_routes_event_to_incident_manager():
    """Test 28: Verifies that consuming a failure event maps fields to the incident ledger [1]."""
    mock_result = {"check_name": "duplicate_records", "status": "FAIL", "failed_records": 5, "message": "Duplicate detected."}
    publish_quality_event(run_id=161, result=mock_result)
    
    processed = consume_event_store_stream(consumer_name="incident_consumer")
    assert processed == 1
    
    with engine.connect() as conn:
        inc_count = conn.execute(text("SELECT COUNT(*) FROM pipeline_incidents WHERE run_id = 161;")).scalar()
        assert inc_count == 1

def test_29_consumer_reprocessing_guarantees_idempotency():
    """Test 29: Asserts that running the consumer twice against the same event avoids duplicate incidents [1]."""
    mock_result = {"check_name": "duplicate_records", "status": "FAIL", "failed_records": 5, "message": "Duplicate."}
    publish_quality_event(run_id=161, result=mock_result)
    
    # First Pass: Processes event and opens an incident [1]
    assert consume_event_store_stream(consumer_name="incident_consumer") == 1
    # Second Pass: The idempotency gate skips execution cleanly [1]
    assert consume_event_store_stream(consumer_name="incident_consumer") == 0
    
    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM pipeline_incidents;")).scalar() == 1

def test_30_unknown_events_fail_safely_without_crashing_worker():
    """Test 30: Confirms that encountering an unmapped event type logs a warning and skips safely [1]."""
    # Emit an unknown event type directly using your producer utility [1]
    emit_pipeline_event(event_type="SOMETHING_UNKNOWN", run_id=161, producer="vague_service", payload={})
    
    try:
        processed = consume_event_store_stream(consumer_name="incident_consumer")
        assert processed == 1
    except Exception as exc:
        pytest.fail(f"Consumer engine crashed on an unexpected event schema: {exc}")
