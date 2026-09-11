from sqlalchemy import text
from src.database import engine


def test_operational_metrics_view_exists():
    """
    ARRANGE, ACT & ASSERT: Queries the PostgreSQL system catalog tables
    to confirm that the pipeline_operational_metrics analytical reporting
    view stands fully created and active on disk.
    """
    query = text("""
        SELECT to_regclass('pipeline_operational_metrics');
    """)

    with engine.connect() as connection:
        result = connection.execute(query).scalar()

    assert result == "pipeline_operational_metrics"
