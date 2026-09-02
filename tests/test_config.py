from src.config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    PIPELINE_NAME,
)


def test_database_configuration_exists():
    """Verify that vital database properties are loaded into system memory."""
    assert DB_HOST is not None
    assert DB_PORT is not None
    assert DB_NAME is not None
    assert DB_USER is not None


def test_pipeline_name_matches_env():
    """Asserts that the loaded pipeline signature matches our project identity."""
    assert PIPELINE_NAME == "uganda_network_intelligence"
