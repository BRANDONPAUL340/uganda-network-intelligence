"""
Uganda Network Intelligence Platform — Lineage Integration Tests
Validates dataset throughput tracking using parameterized fixture factories [INDEX].
"""
import pytest
import pandas as pd
from src.monitoring.lineage import get_run_lineage


def test_run_lineage_query_returns_dataframe(test_run, test_lineage):
    """
    16 & 19. Clean Integration Test: Requests nested fixtures to create an isolated world, 
    executes the application code query, and verifies structure without hardcoded IDs [INDEX].
    """
    # Act: Invoke the active data lineage retrieval engine [INDEX]
    result_df = get_run_lineage(test_run)
    
    # 19. Assertions: Verify structure and values match the specific dynamic test_run ID [INDEX]
    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty
    assert len(result_df) == 1
    
    # Verify that every returned record maps back to the unique dynamic test runner context [INDEX]
    assert result_df["run_id"].astype(int).eq(test_run).all()
