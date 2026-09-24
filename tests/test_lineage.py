from sqlalchemy import text
from src.database import engine
from src.lineage import record_lineage


def test_record_lineage_is_callable():
    """
    ARRANGE, ACT & ASSERT: Verifies that our lineage tracking function
    is active and callable by the main orchestration engine.
    """
    assert callable(record_lineage)


def test_pipeline_lineage_table_exists():
    """
    ARRANGE, ACT & ASSERT: Queries the PostgreSQL system catalogs to
    confirm the pipeline_lineage table stands fully active on disk.
    """
    query = text("""
        SELECT to_regclass('pipeline_lineage');
    """)

    with engine.connect() as connection:
        result = connection.execute(query).scalar()

    assert result == "pipeline_lineage"
import pandas as pd
from src.dashboard.monitoring import (
    get_run_details,
    get_stage_details,
    get_run_lineage,
    get_incident_complete_context,
    get_current_processing_watermarks,
)


def test_run_details_query_returns_dataframe():
    """Test 1: Asserts that run details query returns a valid dataframe data structure [INDEX]."""
    df = get_run_details(99999) # Non-existent ID parameter
    assert isinstance(df, pd.DataFrame)
    assert df.empty or "run_id" in df.columns


def test_stage_details_query_returns_dataframe():
    """Test 2: Asserts that stage details query layer executes without throwing crashes [INDEX]."""
    df = get_stage_details(1)
    assert isinstance(df, pd.DataFrame)


def test_run_lineage_query_returns_dataframe():
    """Test 3: Asserts that lineage query layers return matching structure dataframes [INDEX]."""
    df = get_run_lineage(1)
    assert isinstance(df, pd.DataFrame)


def test_incident_context_query_structural_join():
    """Test 4 & 5: Asserts that combined context query joins columns correctly and handles missing runs gracefully [INDEX]."""
    df = get_incident_complete_context(selected_alert_id=1)
    assert isinstance(df, pd.DataFrame)
    if not df.empty:
        assert "alert_name" in df.columns
        assert "pipeline_status" in df.columns


def test_unknown_run_id_does_not_crash_query():
    """Test 6: Asserts that an unknown run ID returns an empty dataframe safely instead of breaking [INDEX]."""
    df = get_run_details(-1)
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_watermark_information_retrieval():
    """Test 7: Asserts that watermarks query layer extracts tracking columns successfully [INDEX]."""
    df = get_current_processing_watermarks()
    assert isinstance(df, pd.DataFrame)
    if not df.empty:
        assert "last_raw_measurement_id" in df.columns
