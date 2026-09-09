import inspect
from src.pipeline import finish_pipeline_run, update_pipeline_stage


def test_records_processed_default():
    """
    ARRANGE, ACT & ASSERT: Verifies that our pipeline closeout function 
    maintains an interface with a default records_processed count of 0.
    """
    signature = inspect.signature(finish_pipeline_run)
    assert signature.parameters["records_processed"].default == 0


def test_update_pipeline_stage_exists():
    """
    ARRANGE, ACT & ASSERT: Verifies that our real-time stage progression 
    pulsing hook is active and callable by the main module.
    """
    assert callable(update_pipeline_stage)


def test_finish_pipeline_run_exists():
    """
    ARRANGE, ACT & ASSERT: Verifies that our closeout function endpoint 
    is active and callable by the orchestration engine.
    """
    assert callable(finish_pipeline_run)


def test_finish_pipeline_supports_stage():
    """
    ARRANGE, ACT & ASSERT: Verifies that our database closeout script 
    correctly supports the current_stage argument parameter block.
    """
    signature = inspect.signature(finish_pipeline_run)
    assert "current_stage" in signature.parameters
