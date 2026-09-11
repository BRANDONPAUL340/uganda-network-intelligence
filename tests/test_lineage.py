from sqlalchemy import text
from src.database import engine
from src.lineage import record_lineage


def test_record_lineage_is_callable():
    """
    ARRANGE, ACT & ASSERT: Verifies that our lineage tracking function
    is active and callable by the main orchestration engine.
    """
    assert callable(record_lineage)


def test_pipeline_lineage_table_exists():
    """
    ARRANGE, ACT & ASSERT: Queries the PostgreSQL system catalogs to
    confirm the pipeline_lineage table stands fully active on disk.
    """
    query = text("""
        SELECT to_regclass('pipeline_lineage');
    """)

    with engine.connect() as connection:
        result = connection.execute(query).scalar()

    assert result == "pipeline_lineage"
