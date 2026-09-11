from sqlalchemy import text
from src.database import engine


def test_pipeline_audit_report_exists():
    """
    ARRANGE, ACT & ASSERT: Queries the PostgreSQL system catalog to
    confirm the pipeline_audit_report reporting view is active on disk.
    """
    query = text("""
        SELECT to_regclass('pipeline_audit_report');
    """)

    with engine.connect() as connection:
        result = connection.execute(query).scalar()

    assert result == "pipeline_audit_report"
