import pytest
from sqlalchemy import text
from src.database import engine
from src.monitoring.event_store import (
    emit_pipeline_event,
    replay_event_atomically,
    replay_failed_events
)

@pytest.fixture(autouse=True)
def clean_event_and_processing_ledgers():
    """Resets the event store, processing matrix, and pipeline incident tables before each test pass [INDEX]."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE pipeline_event_store RESTART IDENTITY CASCADE;"))
        conn.execute(text("TRUNCATE TABLE event_processing RESTART IDENTITY CASCADE;"))
        conn.execute(text("TRUNCATE TABLE pipeline_incidents RESTART IDENTITY CASCADE;"))
    yield


def test_missing_event_id_is_handled_safely_without_crashing():
    """Asserts that trying to replay a non-existent event ID returns False gracefully instead of crashing [INDEX]."""
    assert replay_event_atomically("00000000-0000-0000-0000-000000000000", consumer_name="incident_consumer") is False


def test_successful_replay_transitions_state_to_processed():
    """Asserts that a successful atomic replay updates the checkpoint status to PROCESSED inside the matrix [INDEX]."""
    evt_id = emit_pipeline_event(
        event_type="QUALITY_CHECK_FAILED", run_id=161, producer="test_producer",
        payload={"check_name": "volume_check", "message": "Volume breached"}
    )
    
    # Execute atomic replay pass [INDEX]
    assert replay_event_atomically(evt_id, consumer_name="incident_consumer") is True
    
    with engine.connect() as conn:
        status = conn.execute(
            text("SELECT status FROM event_processing WHERE event_id = :evt_id;"), {"evt_id": evt_id}
        ).scalar()
        assert status == "PROCESSED"


def test_batch_replay_pulls_and_reprocesses_failed_dead_letter_events():
    """Asserts that batch recovery workers extract and reprocess dead-lettered FAILED entries [INDEX]."""
    evt_id = emit_pipeline_event(
        event_type="QUALITY_CHECK_FAILED", run_id=161, producer="test_producer",
        payload={"check_name": "null_site_id", "message": "Null site ID found"}
    )
    
    # ARRANGE: Simulate a pre-existing dead-letter failure row in event_processing [INDEX]
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO event_processing (event_id, consumer_name, status, attempt_count, error_message) VALUES (:evt_id, 'incident_consumer', 'FAILED', 1, 'Mock network exception');"),
            {"evt_id": evt_id}
        )
        
    # ACT: Invoke the batch dead-letter recovery worker loop [INDEX]
    results = replay_failed_events(consumer_name="incident_consumer")
    
    # ASSERT: The dead-letter event was pulled and re-run successfully [INDEX]
    assert len(results) == 1
    assert results[0]["event_id"] == evt_id
    assert results[0]["success"] is True
