import pytest
from sqlalchemy import text
from src.database import engine
from src.monitoring.event_store import emit_pipeline_event
from src.monitoring.event_worker import run_continuous_worker_service, process_concurrent_event_batch


@pytest.fixture(autouse=True)
def clean_event_and_processing_ledgers():
    """Fixture to reset the event store and processing matrix tables before each test pass [INDEX]."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE pipeline_event_store RESTART IDENTITY CASCADE;"))
        conn.execute(text("TRUNCATE TABLE event_processing RESTART IDENTITY CASCADE;"))
        conn.execute(text("TRUNCATE TABLE pipeline_incidents RESTART IDENTITY CASCADE;"))
    yield


def test_continuous_worker_handles_empty_queues_cleanly():
    """5. Asserts that the continuous daemon loop manages empty event states gracefully without breaking [INDEX]."""
    # Run the worker with a 0.01s interval and exactly 1 loop execution turn to test the exit gate safely [INDEX]
    try:
        run_continuous_worker_service(consumer_name="incident_consumer", poll_interval=0.01, batch_size=10, max_loops=1)
    except Exception as exc:
        pytest.fail(f"Continuous daemon worker crashed on an empty pipeline queue loop: {exc}")


def test_backpressure_batch_size_control_restricts_ingestion_volumes():
    """Tuning Check: Verifies that the worker limits processing limits to the assigned batch size [INDEX]."""
    for i in range(5):
        emit_pipeline_event(
            event_type="QUALITY_CHECK_FAILED", run_id=161, producer="load_generator",
            payload={"check_name": f"volume_check_{i}", "message": "Backpressure check"}
        )
        
    # Restrict batch allocation limits to exactly 2 records per turnaround pass [INDEX]
    metrics = process_concurrent_event_batch(consumer_name="incident_consumer", batch_size=2)
    assert metrics["received"] == 2
    assert metrics["processed"] == 2
