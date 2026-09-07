from src.data_quality import (
    run_data_quality_checks,
)
from src.data_quality.measurements import record_quality_result


def test_quality_functions_exist():
    """
    ARRANGE, ACT & ASSERT: Verifies that our data quality monitoring package
    compiles smoothly and exposes active, callable handler methods.
    """
    assert callable(record_quality_result)
    assert callable(run_data_quality_checks)
