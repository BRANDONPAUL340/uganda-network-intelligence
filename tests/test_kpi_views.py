from sqlalchemy import text
from src.database import engine

EXPECTED_VIEWS = [
    "pipeline_kpis",
    "pipeline_stage_kpis",
    "pipeline_stage_summary",
    "daily_pipeline_health",
    "current_pipeline_health",
]


def test_kpi_views_exist():
    """ARRANGE, ACT & ASSERT: Queries information_schema to verify KPI view visibility [INDEX]."""
    query = text("""
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema = 'public'
          AND table_name = ANY(:view_names);
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {"view_names": EXPECTED_VIEWS},
        ).fetchall()

    existing_views = {row[0] for row in rows}

    for view in EXPECTED_VIEWS:
        assert view in existing_views, f"Dashboard view '{view}' is missing from public schema catalog."
