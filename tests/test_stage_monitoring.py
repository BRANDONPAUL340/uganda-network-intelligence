from src.monitoring import start_stage_run, finish_stage_run


def test_stage_monitoring_methods_are_callable():
    """
    ARRANGE, ACT & ASSERT: Verifies that our stage monitoring package sub-modules
    compile cleanly and expose active, callable handler methods.
    """
    assert callable(start_stage_run)
    assert callable(finish_stage_run)
