from sqlalchemy import text
from src.database import engine


def test_silver_site_date_index_exists():
    """ARRANGE, ACT & ASSERT: Audits the database catalog to ensure idx_silver_site_date is active on disk [INDEX]."""
    query = text("""
        SELECT 1
        FROM pg_indexes
        WHERE schemaname = 'public'
          AND tablename = 'silver_measurements'
          AND indexname = 'idx_silver_site_date';
    """)

    with engine.connect() as connection:
        result = connection.execute(query).scalar_one_or_none()

    assert result == 1
