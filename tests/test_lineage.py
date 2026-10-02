"""
Uganda Network Intelligence Platform — Parameterized Lineage Integration Tests
Validates dataset throughput tracking across various pipeline states and edge cases [INDEX].
"""
import pytest
import pandas as pd
from src.monitoring.lineage import get_run_lineage
from tests.factories import create_test_run_factory, create_test_lineage_factory


@pytest.mark.parametrize(
    "status, current_stage",
    [
        ("RUNNING", "BRONZE"),
        ("SUCCESS", "GOLD"),
        ("FAILED", "SILVER"),
    ],
    ids=["active_stage", "completed_stage", "failed_stage"], # 18. Provide readable IDs [INDEX]
)
@pytest.mark.parametrize(
    "records_affected",
,
    ids=["zero_boundary", "nominal_volume"],
)
def test_lineage_retrieval_across_multiple_pipeline_states(
    db_connection, status, current_stage, records_affected
):
    """
    19, 21 & 25. Multi-Dimensional State Test: Generates 6 distinct test scenarios 
    automatically via stacked decorators, combining connection fixtures and data factories cleanly [INDEX].
    """
    # 22. Parameter + Fixture + Factory: Pass parameters straight down into factory metrics [INDEX]
    run_id = create_test_run_factory(
        db_connection, 
        status=status, 
        current_stage=current_stage,
        pipeline_name=f"pytest_parameterized_{status.lower()}"
    )
    
    # 25. Seed explicit record volumes linked back to the parental run_id [INDEX]
    create_test_lineage_factory(
        db_connection, 
        run_id=run_id, 
        target_table="silver_measurements", 
        records_affected=records_affected
    )
    
    # Act: Invoke the active data lineage retrieval engine, injecting the shared connection context [INDEX]
    result_df = get_run_lineage(run_id, connection=db_connection)
    
    # Assertions: Verify structure and values match our physical database contracts precisely [INDEX]
    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty
    assert len(result_df) == 1
    
    # 25. Contract Assertions: Assert returned values match the explicit parameterized inputs [INDEX]
    assert result_df["run_id"].astype(int).eq(run_id).all()
    assert int(result_df.iloc[0]["records_affected"]) == records_affected
