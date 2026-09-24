import pandas as pd
from src.dashboard.monitoring import (
    get_recent_runs,
    get_failed_runs,
    get_failed_steps,
    get_run_summary,
    get_last_successful_run
)


def test_get_recent_runs_returns_dataframe():
    """ARRANGE, ACT & ASSERT: Verifies recent runs query structure."""
    result = get_recent_runs()
    assert isinstance(result, pd.DataFrame)


def test_get_failed_steps_returns_dataframe_with_columns():
    """ARRANGE, ACT & ASSERT: Verifies failed steps layer maps structural columns safely."""
    result = get_failed_steps()
    assert isinstance(result, pd.DataFrame)
    if not result.empty:
        assert "run_id" in result.columns
        assert "step_name" in result.columns


def test_get_run_summary_returns_dataframe():
    """ARRANGE, ACT & ASSERT: Verifies KPI card aggregator return profile."""
    result = get_run_summary()
    assert isinstance(result, pd.DataFrame)
    if not result.empty:
        assert "total_runs" in result.columns


def test_get_last_successful_run_returns_dataframe():
    """ARRANGE, ACT & ASSERT: Verifies high-watermark run data layout."""
    result = get_last_successful_run()
    assert isinstance(result, pd.DataFrame)
def test_get_available_runs_returns_dataframe():
    """ARRANGE, ACT & ASSERT: Verifies dropdown index list returns a valid pandas DataFrame [INDEX]."""
    from src.dashboard.monitoring import get_available_runs
    result = get_available_runs()
    assert isinstance(result, pd.DataFrame)


def test_get_run_steps_returns_dataframe_with_expected_schema():
    """ARRANGE, ACT & ASSERT: Verifies parameterized sub-stage lookups map core tracking columns [INDEX]."""
    from src.dashboard.monitoring import get_run_steps
    # Query with baseline run context ID 161
    result = get_run_steps(161)
    assert isinstance(result, pd.DataFrame)
    if not result.empty:
        assert "run_id" in result.columns
        assert "step_name" in result.columns
        assert "status" in result.columns
def test_get_run_steps_with_unknown_id_returns_empty_dataframe():
    """ARRANGE, ACT & ASSERT: Verifies that a non-existent run_id returns an empty DataFrame instead of crashing [INDEX]."""
    from src.dashboard.monitoring import get_run_steps
    
    # Query using an out-of-bounds mock ID parameter
    result = get_run_steps(999999)
    
    assert isinstance(result, pd.DataFrame)
    assert result.empty is True
