from sqlalchemy import text

from src.database import engine


def test_silver_measurements_exist():
    """Verify that your enriched Silver measurements layer is populated and active."""
    sql = "SELECT COUNT(*) FROM silver_measurements;"
    with engine.connect() as connection:
        count = connection.execute(text(sql)).scalar()
    assert count > 0


def test_silver_measurements_are_unique():
    """
    Directly tests your Day 25 idempotency architecture.
    Asserts that zero duplicate measurement_id records exist inside the Silver layer.
    """
    sql = """
    SELECT COUNT(*)
    FROM (
        SELECT measurement_id
        FROM silver_measurements
        GROUP BY measurement_id
        HAVING COUNT(*) > 1
    ) duplicates;
    """
    with engine.connect() as connection:
        duplicate_count = connection.execute(text(sql)).scalar()
    assert duplicate_count == 0


def test_silver_network_health_exists():
    """Verify that your feature-calculated Silver network health layer contains data."""
    sql = """
    SELECT COUNT(*)
    FROM silver_network_health;
    """
    with engine.connect() as connection:
        count = connection.execute(text(sql)).scalar()
    assert count > 0


def test_network_health_status_is_valid():
    """
    Asserts that the feature categorization logic maps values strictly 
    within our corporate domain rules matrix.
    """
    sql = """
    SELECT COUNT(*)
    FROM silver_network_health
    WHERE health_status NOT IN (
        'Healthy',
        'Warning',
        'Critical'
    );
    """
    with engine.connect() as connection:
        invalid_count = connection.execute(text(sql)).scalar()
    assert invalid_count == 0


def test_gold_site_performance_exists():
    """Verify that your analytical Gold site daily performance layer is active."""
    sql = """
    SELECT COUNT(*)
    FROM gold_site_daily_performance;
    """
    with engine.connect() as connection:
        count = connection.execute(text(sql)).scalar()
    assert count > 0


def test_gold_equipment_health_exists():
    """Verify that your analytical Gold equipment hardware metrics matrix contains data."""
    sql = """
    SELECT COUNT(*)
    FROM gold_equipment_health;
    """
    with engine.connect() as connection:
        count = connection.execute(text(sql)).scalar()
    assert count > 0


def test_gold_health_status_is_valid():
    """
    Asserts that Gold hardware aggregations do not contain any unmapped 
    or unexpected status classification errors.
    """
    sql = """
    SELECT COUNT(*)
    FROM gold_equipment_health
    WHERE health_status NOT IN (
        'Healthy',
        'Warning',
        'Critical'
    );
    """
    with engine.connect() as connection:
        invalid_count = connection.execute(text(sql)).scalar()
    assert invalid_count == 0
def test_pipeline_runs_exist():
    """Verify that your operational pipeline run tracking ledger is active."""
    sql = """
    SELECT COUNT(*)
    FROM pipeline_runs;
    """
    with engine.connect() as connection:
        count = connection.execute(text(sql)).scalar()
    assert count > 0


def test_pipeline_has_valid_status():
    """
    Asserts that the system logs write structural states strictly 
    within our standard data ops rules.
    """
    sql = """
    SELECT COUNT(*)
    FROM pipeline_runs
    WHERE status NOT IN (
        'RUNNING',
        'SUCCESS',
        'FAILED'
    );
    """
    with engine.connect() as connection:
        invalid_count = connection.execute(text(sql)).scalar()
    assert invalid_count == 0
