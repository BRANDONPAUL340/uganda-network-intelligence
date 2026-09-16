from sqlalchemy import text
from src.database import engine


def test_watermark_has_stage_column():
    """ARRANGE, ACT & ASSERT: Audits the database system catalog to ensure stage column is active."""
    query = text("""
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'processing_watermarks'
          AND column_name = 'stage_name';
    """)

    with engine.connect() as connection:
        result = connection.execute(query).scalar_one_or_none()

    assert result == 1
