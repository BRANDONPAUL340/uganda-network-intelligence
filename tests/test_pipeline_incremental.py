from src.pipeline_incremental import run_pipeline_incremental


def test_master_incremental_pipeline_is_callable():
    """ARRANGE, ACT & ASSERT: Verifies the master incremental supervisor engine loop is fully callable."""
    assert callable(run_pipeline_incremental)
