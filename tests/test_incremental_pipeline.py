from src.pipeline_incremental import run_incremental_pipeline


def test_incremental_pipeline_is_callable():
    """ARRANGE, ACT & ASSERT: Verifies the master incremental pipeline supervisor is fully callable."""
    assert callable(run_incremental_pipeline)
