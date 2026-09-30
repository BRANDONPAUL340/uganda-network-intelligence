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


def test_consumer_correctly_processes_legacy_v1_event_payloads():
    """6 & 11. Asserts that legacy Version 1.0.0 layout contracts pass safely [INDEX]."""
    v1_id = emit_pipeline_event(
        event_type="QUALITY_CHECK_FAILED", run_id=161, producer="legacy_engine", event_version="1.0.0",
        payload={"check_name": "volume_check", "status": "FAIL", "failed_records": 10, "message": "V1 Alert Message"}
    )
    assert replay_event_atomically(v1_id, consumer_name="incident_consumer") is True
    
    with engine.connect() as conn:
        inc = conn.execute(text("SELECT check_name, message FROM pipeline_incidents;")).fetchone()
        assert inc.check_name == "volume_check"
        assert inc.message == "V1 Alert Message"


def test_consumer_correctly_processes_graduated_v2_event_payloads():
    """7 & 11. Asserts that graduated Version 2.0.0 contracts parse successfully without KeyErrors [INDEX]."""
    v2_id = emit_pipeline_event(
        event_type="QUALITY_CHECK_FAILED", run_id=161, producer="modern_engine", event_version="2.0.0",
        payload={"check": "freshness_check", "severity": "MEDIUM", "error_description": "V2 Refactored Message"}
    )
    assert replay_event_atomically(v2_id, consumer_name="incident_consumer") is True
    
    with engine.connect() as conn:
        inc = conn.execute(text("SELECT check_name, message, severity FROM pipeline_incidents;")).fetchone()
        assert inc.check_name == "freshness_check"
        assert inc.message == "V2 Refactored Message"
        assert inc.severity == "MEDIUM"
def test_unsupported_event_version_fails_safely_and_logs_to_dead_letter_queue():
    """14 & 15. Asserts that receiving an unsupported Version 3.0.0 packet drops to FAILED state safely [INDEX]."""
    v3_id = emit_pipeline_event(
        event_type="QUALITY_CHECK_FAILED", run_id=161, producer="future_engine", event_version="3.0.0",
        payload={"v3_broken_key": "Out of bounds contract layout structure"}
    )
    
    # The atomic replay driver captures the NotImplementedError exception and logs it [INDEX]
    assert replay_event_atomically(v3_id, consumer_name="incident_consumer") is False
    
    with engine.connect() as conn:
        status = conn.execute(
            text("SELECT status, error_message FROM event_processing WHERE event_id = :evt_id;"), {"evt_id": v3_id}
        ).fetchone()
        assert status.status == "FAILED"
        assert "Unsupported Contract Rule" in status.error_message
