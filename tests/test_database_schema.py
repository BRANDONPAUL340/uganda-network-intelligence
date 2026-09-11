from sqlalchemy import text
from src.database import engine


def test_core_tables_exist():
    """
    ARRANGE, ACT & ASSERT: Queries the PostgreSQL system information catalog
    to verify that all 11 core staging, Silver, Gold, and telemetry tracking
    tables exist on disk.
    """
    tables = {
        "sites",
        "equipment",
        "measurements",
        "incidents",
        "silver_measurements",
        "silver_network_health",
        "gold_site_daily_performance",
        "gold_equipment_health",
        "pipeline_runs",
        "pipeline_stage_runs",
        "pipeline_lineage",
    }

    query = text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public';
    """)

    with engine.connect() as connection:
        existing_tables = {
            row[0]
            for row in connection.execute(query).fetchall()
        }

    # Verify that our expected tables are a subset of what actually exists in the DB
    assert tables.issubset(existing_tables)
