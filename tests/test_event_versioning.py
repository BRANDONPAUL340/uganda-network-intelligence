import pytest
from sqlalchemy import text
from src.database import engine
from src.monitoring.event_store import emit_pipeline_event, replay_event_atomically


@pytest.fixture(autouse=True)
def clean_event_and_incident_ledgers():
    """Fixture to ensure isolation before running version-handling test sweeps [INDEX]."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE pipeline_event_store RESTART IDENTITY CASCADE;"))
        conn.execute(text("TRUNCATE TABLE event_processing RESTART IDENTITY CASCADE;"))
        conn.execute(text("TRUNCATE TABLE pipeline_incidents RESTART IDENTITY CASCADE;"))
    yield


def test_25_quality_failure_v1_is_supported_and_uses_v1_handler():
    """Test 25: Asserts that legacy Version 1 layout contracts pass safely and trigger V1 handlers [INDEX]."""
    v1_id = emit_pipeline_event(
        event_type="QUALITY_CHECK_FAILED", run_id=161, producer="legacy_engine", event_version="1.0.0",
        payload={"check_name": "volume_check", "status": "FAIL", "failed_records": 10, "message": "V1 Alert Message"}
    )
    assert replay_event_atomically(v1_id, consumer_name="incident_consumer") is True
    
    with engine.connect() as conn:
        inc = conn.execute(text("SELECT check_name, message, severity FROM pipeline_incidents;")).fetchone()
        assert inc.check_name == "volume_check"
        assert inc.message == "V1 Alert Message"
        assert inc.severity == "HIGH"  # Enforces V1 default baseline fallback [INDEX]


def test_25_quality_failure_v2_is_supported_and_uses_v2_handler():
    """Test 25: Asserts that graduated Version 2.0.0 contracts parse successfully without KeyErrors [INDEX]."""
    v2_id = emit_pipeline_event(
        event_type="QUALITY_CHECK_FAILED", run_id=161, producer="modern_engine", event_version="2.0.0",
        payload={"check": "freshness_check", "severity": "MEDIUM", "error_description": "V2 Refactored Message"}
    )
    assert replay_event_atomically(v2_id, consumer_name="incident_consumer") is True
    
    with engine.connect() as conn:
        inc = conn.execute(text("SELECT check_name, message, severity FROM pipeline_incidents;")).fetchone()
        assert inc.check_name == "freshness_check"
        assert inc.message == "V2 Refactored Message"
        assert inc.severity == "MEDIUM"  # Captures newly introduced field parameter [INDEX]


def test_25_unknown_event_version_fails_safely_and_logs_to_dead_letter_queue():
    """Test 25 & 27: Asserts that receiving an unsupported Version variant fails safely without crashing the thread [INDEX]."""
    v_unknown_id = emit_pipeline_event(
        event_type="QUALITY_CHECK_FAILED", run_id=161, producer="future_engine", event_version="99.0.0",
        payload={"v99_broken_key": "Out of bounds contract layout structure"}
    )
    
    # The atomic replay driver captures the exception and logs a failure checkpoint cleanly [INDEX]
    assert replay_event_atomically(v_unknown_id, consumer_name="incident_consumer") is False
    
    with engine.connect() as conn:
        status = conn.execute(
            text("SELECT status, error_message FROM event_processing WHERE event_id = :evt_id;"), {"evt_id": v_unknown_id}
        ).fetchone()
        assert status.status == "FAILED"
        assert "Unsupported Contract Rule" in status.error_message


def test_25_reprocessing_same_event_version_guarantees_idempotency_protection():
    """Test 25: Asserts that replaying the exact same event token twice skips redundant incident replication [INDEX]."""
    v2_id = emit_pipeline_event(
        event_type="QUALITY_CHECK_FAILED", run_id=161, producer="modern_engine", event_version="2.0.0",
        payload={"check": "duplicate_records", "severity": "HIGH", "error_description": "Duplicate values detected."}
    )
    
    # First Pass: Processes event contract and opens an incident on disk [INDEX]
    assert replay_event_atomically(v2_id, consumer_name="incident_consumer") is True
    
    # Second Pass: The idempotency gate check fires, updating counters without duplicating row tickets [INDEX]
    assert replay_event_atomically(v2_id, consumer_name="incident_consumer") is True
    
    with engine.connect() as conn:
        # Assert that your incident row volume hasn't shifted, confirming downstream protection [INDEX]
        inc_count = conn.execute(text("SELECT COUNT(*) FROM pipeline_incidents;")).scalar()
        assert inc_count == 1
        
        # Assert that the incident occurrence frequency has updated correctly [INDEX]
        occ_count = conn.execute(text("SELECT occurrence_count FROM pipeline_incidents;")).scalar()
        assert occ_count == 2
