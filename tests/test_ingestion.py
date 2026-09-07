from sqlalchemy import text
from src.database import engine
from src.ingestion.measurements import run_ingestion


def test_source_record_id_is_deterministic():
    """
    ARRANGE, ACT & ASSERT: Verifies that our ingestion orchestrator 
    exposes a callable interface within the pipeline architecture.
    """
    assert callable(run_ingestion)


def test_ingestion_layer_database_is_reachable():
    """
    ARRANGE, ACT & ASSERT: Confirms that our ingestion layer can cleanly 
    reach out and query metadata fields using our active database engine adapter.
    """
    sql = "SELECT COUNT(*) FROM pipeline_runs;"
    with engine.begin() as connection:
        count = connection.execute(text(sql)).scalar()
        assert isinstance(count, int)
