from sqlalchemy import text
from src.database import engine


def test_incremental_processing_view_exists():
    """ARRANGE, ACT & ASSERT: Audits the database system catalog to ensure the monitor view stands active."""
    query = text("""
        SELECT 1
        FROM information_schema.views
        WHERE table_name = 'incremental_processing_status';
    """)

    with engine.connect() as connection:
        result = connection.execute(query).scalar_one_or_none()

    assert result == 1
