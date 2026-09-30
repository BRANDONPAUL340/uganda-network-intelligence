import pytest
import pandas as pd
from sqlalchemy import text
from src.database import engine
from src.dashboard.monitoring import get_unified_event_processing_telemetry, get_worker_nodes_heartbeat_ledger


@pytest.fixture(autouse=True)
def clean_observability_state_ledgers():
    """Fixture to ensure a completely empty data table environment to stress test edge cases safely [INDEX]."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE event_processing RESTART IDENTITY CASCADE;"))
        conn.execute(text("TRUNCATE TABLE pipeline_worker_heartbeats RESTART IDENTITY CASCADE;"))
    yield


def test_empty_event_system_calculates_failure_metrics_safely_without_division_by_zero():
    """Part 21. Edge Case Test: Verifies that zero processing records are handled safely without a ZeroDivisionError [INDEX]."""
    df = get_unified_event_processing_telemetry()
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    # Unpack first row parameters
    row = df.iloc[0]
    assert int(row["total_records"]) == 0
    assert float(row["failure_rate_pct"]) is None or pd.isna(row["failure_rate_pct"]) or float(row["failure_rate_pct"]) == 0.0


def test_empty_heartbeats_returns_empty_dataframe_gracefully():
    """Part 21. Edge Case Test: Verifies that an empty heartbeat catalog handles zero active workers safely [INDEX]."""
    df = get_worker_nodes_heartbeat_ledger()
    assert isinstance(df, pd.DataFrame)
    assert df.empty is True
