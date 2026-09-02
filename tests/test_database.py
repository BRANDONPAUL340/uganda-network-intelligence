from sqlalchemy import text

from src.database import engine


def test_database_connection():
    """
    ARRANGE, ACT & ASSERT: Verifies that our python environment can 
    successfully establish a low-level network connection link to 
    the PostgreSQL instance and execute basic query statements.
    """
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT 1")
        )
        assert result.scalar() == 1


def test_core_tables_exist():
    """
    ARRANGE, ACT & ASSERT: Programmatically queries the database information 
    schema catalog to verify that all core transactional staging and reference 
    tables are fully standing and accessible on disk.
    """
    required_tables = {
        "sites",
        "equipment",
        "measurements",
        "incidents",
    }

    sql = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public';
    """

    with engine.connect() as connection:
        result = connection.execute(text(sql))
        existing_tables = {
            row[0]
            for row in result
        }

    assert required_tables.issubset(existing_tables)


def test_pipeline_tables_exist():
    """
    ARRANGE, ACT & ASSERT: Programmatically verifies that all processed Medallion 
    tier storage spaces (Silver enrichment, Gold aggregates, and logging diaries) 
    are properly provisioned on disk.
    """
    required_tables = {
        "pipeline_runs",
        "silver_measurements",
        "silver_network_health",
        "gold_site_daily_performance",
        "gold_equipment_health",
    }

    sql = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public';
    """

    with engine.connect() as connection:
        result = connection.execute(text(sql))
        existing_tables = {
            row[0]
            for row in result
        }

    assert required_tables.issubset(existing_tables)
