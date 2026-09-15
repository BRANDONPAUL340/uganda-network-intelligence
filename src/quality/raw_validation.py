import logging
from sqlalchemy import text
from src.database import engine

logger = logging.getLogger(__name__)


def check_raw_measurement_count():
    """Returns the total number of records in the RAW landing layer."""
    query = text("SELECT COUNT(*) FROM raw_measurements;")

    with engine.connect() as connection:
        return connection.execute(query).scalar_one()


def check_raw_null_measurement_ids():
    """Checks for RAW records missing their measurement identifier."""
    query = text("""
        SELECT COUNT(*)
        FROM raw_measurements
        WHERE measurement_id IS NULL;
    """)

    with engine.connect() as connection:
        return connection.execute(query).scalar_one()


def check_raw_invalid_measurements():
    """Checks RAW telemetry for invalid numerical values."""
    query = text("""
        SELECT COUNT(*)
        FROM raw_measurements
        WHERE
            traffic_mb < 0
            OR latency_ms < 0
            OR packet_loss_pct < 0
            OR packet_loss_pct > 100
            OR signal_strength_dbm > 0
            OR availability_pct < 0
            OR availability_pct > 100;
    """)

    with engine.connect() as connection:
        return connection.execute(query).scalar_one()


def check_raw_missing_site_reference():
    """Checks RAW records with missing site references."""
    query = text("""
        SELECT COUNT(*)
        FROM raw_measurements r
        LEFT JOIN sites s
            ON r.site_id = s.site_id
        WHERE s.site_id IS NULL;
    """)

    with engine.connect() as connection:
        return connection.execute(query).scalar_one()


def check_raw_missing_equipment_reference():
    """Checks RAW records with missing equipment references."""
    query = text("""
        SELECT COUNT(*)
        FROM raw_measurements r
        LEFT JOIN equipment e
            ON r.equipment_id = e.equipment_id
        WHERE e.equipment_id IS NULL;
    """)

    with engine.connect() as connection:
        return connection.execute(query).scalar_one()


def check_raw_duplicates():
    """Checks for duplicate RAW measurement identifiers."""
    query = text("""
        SELECT COUNT(*)
        FROM (
            SELECT measurement_id
            FROM raw_measurements
            GROUP BY measurement_id
            HAVING COUNT(*) > 1
        ) duplicates;
    """)

    with engine.connect() as connection:
        return connection.execute(query).scalar_one()


def run_raw_quality_checks():
    """Runs the complete RAW-layer data quality validation suite."""
    logger.info("Starting RAW data quality checks...")

    metrics = {
        "raw_measurement_count": check_raw_measurement_count(),
        "missing_measurement_id": check_raw_null_measurement_ids(),
        "invalid_raw_measurements": check_raw_invalid_measurements(),
        "invalid_site_reference": check_raw_missing_site_reference(),
        "invalid_equipment_reference": check_raw_missing_equipment_reference(),
        "duplicate_raw_measurements": check_raw_duplicates(),
    }

    logger.info("RAW data quality checks complete.")

    return metrics