from src.logger import get_logger


def test_logger_exists():
    """
    ARRANGE, ACT & ASSERT: Verifies that our logger factory utility 
    initialises properly and returns an active logging instance.
    """
    logger = get_logger("test_context")
    assert logger is not None
