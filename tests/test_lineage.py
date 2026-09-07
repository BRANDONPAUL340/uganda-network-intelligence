from src.monitoring import record_lineage


def test_lineage_function_exists():
    """
    ARRANGE, ACT & ASSERT: Verifies that our data lineage recording package
    compiles smoothly and exposes an active, callable handler method.
    """
    assert callable(record_lineage)
