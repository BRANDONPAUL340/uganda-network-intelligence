from sqlalchemy import text
from src.database import engine


def test_pipeline_kpis_have_valid_rates():
    """ARRANGE, ACT & ASSERT: Verifies that aggregated success and health rates are logically bounded [INDEX]."""
    query = text("""
        SELECT
            pipeline_success_rate,
            healthy_percentage
        FROM pipeline_kpis;
    """)

    with engine.connect() as connection:
        rows = connection.execute(query).fetchall()

    for row in rows:
        if row[0] is not None:
            assert 0 <= float(row[0]) <= 100, f"Invalid pipeline success rate calculated: {row[0]}"

        if row[1] is not None:
            assert 0 <= float(row[1]) <= 100, f"Invalid healthy percentage calculated: {row[1]}"
