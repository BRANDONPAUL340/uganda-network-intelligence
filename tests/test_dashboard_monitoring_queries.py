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
