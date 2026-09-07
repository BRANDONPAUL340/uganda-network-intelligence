from src.data_quality import run_quality_gate


def test_quality_gate_function_is_callable():
    """
    ARRANGE, ACT & ASSERT: Verifies that our core data quality monitoring package
    compiles smoothly and exposes an active, callable run_quality_gate method.
    """
    assert callable(run_quality_gate)
