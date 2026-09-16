from sqlalchemy import text
from src.database import engine


def test_stage_watermark_view_exists():
    """ARRANGE, ACT & ASSERT: Audits the database system catalog to ensure the stage monitor view stands active."""
    query = text("""
        SELECT 1
        FROM information_schema.views
        WHERE table_name = 'stage_watermark_status';
    """)

    with engine.connect() as connection:
        result = connection.execute(query).scalar_one_or_none()

    assert result == 1
