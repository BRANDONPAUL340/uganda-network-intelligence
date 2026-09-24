import pytest
from sqlalchemy import text
from src.database import engine
from src.pipeline_monitoring import (
    start_pipeline_step,
    complete_pipeline_step,
    fail_pipeline_step,
)


@pytest.fixture(autouse=True)
def clean_pipeline_steps():
    """Fixture to ensure the pipeline_steps table is clean before each test pass [INDEX]."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE pipeline_steps RESTART IDENTITY CASCADE;"))
    yield


def test_start_pipeline_step_creates_running_record():
    """ARRANGE, ACT & ASSERT: Verifies that start_pipeline_step generates a valid ID and sets status to RUNNING [INDEX]."""
    # Using run_id=161 as our known active database baseline run context
    step_id = start_pipeline_step(161, "unit_test_bronze")
    assert isinstance(step_id, int)
    assert step_id > 0

    query = text("SELECT status, step_name FROM pipeline_steps WHERE step_id = :step_id;")
    with engine.connect() as conn:
        row = conn.execute(query, {"step_id": step_id}).fetchone()
        assert row is not None
        assert row._mapping["status"] == "RUNNING"
        assert row._mapping["step_name"] == "unit_test_bronze"


def test_complete_pipeline_step_updates_to_success():
    """ARRANGE, ACT & ASSERT: Verifies that complete_pipeline_step transitions status to SUCCESS and stores record counts [INDEX]."""
    step_id = start_pipeline_step(161, "unit_test_silver")
    complete_pipeline_step(step_id, records_processed=500)

    query = text("SELECT status, records_processed, completed_at FROM pipeline_steps WHERE step_id = :step_id;")
    with engine.connect() as conn:
        row = conn.execute(query, {"step_id": step_id}).fetchone()
        assert row is not None
        assert row._mapping["status"] == "SUCCESS"
        assert row._mapping["records_processed"] == 500
        assert row._mapping["completed_at"] is not None


def test_fail_pipeline_step_updates_to_failed_and_logs_error():
    """ARRANGE, ACT & ASSERT: Verifies that fail_pipeline_step transitions status to FAILED and stores error trace snippets [INDEX]."""
    step_id = start_pipeline_step(161, "unit_test_gold")
    fail_pipeline_step(step_id, error_message="Column alignment mismatch")

    query = text("SELECT status, error_message, completed_at FROM pipeline_steps WHERE step_id = :step_id;")
    with engine.connect() as conn:
        row = conn.execute(query, {"step_id": step_id}).fetchone()
        assert row is not None
        assert row._mapping["status"] == "FAILED"
        assert row._mapping["error_message"] == "Column alignment mismatch"
        assert row._mapping["completed_at"] is not None
