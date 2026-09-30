import pytest
from sqlalchemy import text
from src.database import engine
from src.monitoring.event_store import emit_pipeline_event
from src.monitoring.event_lifecycle import archive_and_purge_batch_cycle


@pytest.fixture(autouse=True)
def clean_observability_state_ledgers():
    """Fixture to ensure clean, isolated data states before each lifecycle test pass [INDEX]."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE pipeline_event_store RESTART IDENTITY CASCADE;"))
        conn.execute(text("TRUNCATE TABLE event_processing RESTART IDENTITY CASCADE;"))
        conn.execute(text("TRUNCATE TABLE pipeline_event_archive RESTART IDENTITY CASCADE;"))
    yield


def test_28_recent_events_are_kept_safely_inside_hot_store():
    """Test 2: Asserts that recent events inside the retention period are kept [INDEX]."""
    evt_id = emit_pipeline_event("QUALITY_CHECK_FAILED", 161, "quality_engine", {"check_name": "freshness"})
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO event_processing (event_id, consumer_name, status) VALUES (:evt_id, 'incident_consumer', 'PROCESSED');"), {"evt_id": evt_id})
        
    # Run cleanup loop. Since the event is brand new, it must be skipped [INDEX]
    metrics = archive_and_purge_batch_cycle(retention_interval_days=30, dry_run=False)
    assert metrics["events_selected"] == 0
    assert metrics["events_archived"] == 0


def test_28_dry_run_reports_metrics_without_modifying_database():
    """Test 3: Asserts that dry_run=True reports summary metrics without changing tables [INDEX]."""
    evt_id = emit_pipeline_event("QUALITY_CHECK_FAILED", 161, "quality_engine", {"check_name": "freshness"})
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO event_processing (event_id, consumer_name, status) VALUES (:evt_id, 'incident_consumer', 'PROCESSED');"), {"evt_id": evt_id})
        conn.execute(text("UPDATE pipeline_event_store SET event_time = CURRENT_TIMESTAMP - INTERVAL '40 days';"))
        
    # Run cleanup loop with dry_run=True [INDEX]
    metrics = archive_and_purge_batch_cycle(retention_interval_days=30, dry_run=True)
    assert metrics["events_selected"] == 1
    assert metrics["events_archived"] == 0
    assert metrics["events_deleted"] == 0
    
    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM pipeline_event_store;")).scalar() == 1
        assert conn.execute(text("SELECT COUNT(*) FROM pipeline_event_archive;")).scalar() == 0


def test_28_empty_queue_is_safe():
    """Test 7: Asserts that running cleanup on an empty table returns safely without exceptions [INDEX]."""
    metrics = archive_and_purge_batch_cycle(retention_interval_days=30, dry_run=False)
    assert metrics["events_selected"] == 0
    assert metrics["events_archived"] == 0
    assert metrics["events_deleted"] == 0
