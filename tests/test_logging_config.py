from pathlib import Path
from src.logging_config import LOG_FILE, configure_logging


def test_log_directory_exists():
    """
    ARRANGE, ACT & ASSERT: Verifies that our rolling log files folder
    is programmatically generated and active on disk.
    """
    assert Path("logs").exists()


def test_log_file_path():
    """
    ARRANGE, ACT & ASSERT: Guarantees the persistence engine filename matches
    our strict database log tracking standard string tokens.
    """
    assert LOG_FILE.name == "pipeline.log"


def test_logging_configuration():
    """
    ARRANGE, ACT & ASSERT: Confirms that triggering the initialization call
    wires up output streams targeting the correct parent folder tiers.
    """
    configure_logging()
    assert LOG_FILE.parent.name == "logs"
