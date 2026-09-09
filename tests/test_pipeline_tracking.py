import inspect
from src.pipeline import finish_pipeline_run


def test_records_processed_default():
    """
    ARRANGE, ACT & ASSERT: Verifies that our pipeline closeout function 
    maintains an interface with a default records_processed count of 0.
    """
    signature = inspect.signature(finish_pipeline_run)

    assert signature.parameters["records_processed"].default == 0
