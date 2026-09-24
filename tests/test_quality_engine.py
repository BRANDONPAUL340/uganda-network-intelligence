import pytest
from sqlalchemy import text
from src.database import engine
from src.monitoring.quality_engine import execute_data_quality_suite


@pytest.fixture(autouse=True)
def clean_quality_logs():
    """Fixture to reset the quality logs ledger table state before each pass [INDEX]."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE data_quality_results RESTART IDENTITY CASCADE;"))
    yield


def test_data_quality_suite_execution_returns_boolean():
    """ARRANGE, ACT & ASSERT: Verifies the quality engine executes smoothly and returns a state flag [INDEX]."""
    # Using run_id=161 as our known active parent database execution baseline
    status = execute_data_quality_suite(161)
    assert isinstance(status, bool)

    # Confirm rows are actively stored in the ledger table
    query = text("SELECT COUNT(*) FROM data_quality_results;")
    with engine.connect() as conn:
        count = conn.execute(query).scalar()
        assert count > 0
