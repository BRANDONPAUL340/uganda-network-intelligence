from sqlalchemy import text

from src.database import engine
from src.logger import get_logger

# Initialize our module-level logger instance
logger = get_logger(__name__)


def check_null_values():
    """
    Check for required fields that contain NULL values.
    """

    sql = """
    SELECT COUNT(*)
    FROM measurements
    WHERE
        equipment_id IS NULL
        OR site_id IS NULL
        OR measured_at IS NULL;
    """

    with engine.begin() as connection:
        result = connection.execute(text(sql))
        count = result.scalar()

    return count


def check_invalid_availability():
    """
    Availability must be between 0 and 100 percent.
    """

    sql = """
    SELECT COUNT(*)
    FROM measurements
    WHERE
        availability_pct < 0
        OR availability_pct > 100;
    """

    with engine.begin() as connection:
        result = connection.execute(text(sql))
        count = result.scalar()

    return count


def check_invalid_packet_loss():
    """
    Packet loss must be between 0 and 100 percent.
    """

    sql = """
    SELECT COUNT(*)
    FROM measurements
    WHERE
        packet_loss_pct < 0
        OR packet_loss_pct > 100;
    """

    with engine.begin() as connection:
        result = connection.execute(text(sql))
        count = result.scalar()

    return count


def check_invalid_latency():
    """
    Latency cannot be negative.
    """

    sql = """
    SELECT COUNT(*)
    FROM measurements
    WHERE latency_ms < 0;
    """

    with engine.begin() as connection:
        result = connection.execute(text(sql))
        count = result.scalar()

    return count


def check_invalid_signal():
    """
    Signal strength cannot be positive in this project.
    """

    sql = """
    SELECT COUNT(*)
    FROM measurements
    WHERE signal_strength_dbm > 0;
    """

    with engine.begin() as connection:
        result = connection.execute(text(sql))
        count = result.scalar()

    return count


def check_orphan_measurements():
    """
    Every measurement must reference an existing
    site and equipment record.
    """

    sql = """
    SELECT COUNT(*)
    FROM measurements m

    LEFT JOIN sites s
        ON m.site_id = s.site_id

    LEFT JOIN equipment e
        ON m.equipment_id = e.equipment_id

    WHERE
        s.site_id IS NULL
        OR e.equipment_id IS NULL;
    """

    with engine.begin() as connection:
        result = connection.execute(text(sql))
        count = result.scalar()

    return count


def run_quality_checks():
    """
    Run all data quality checks.

    Raises an exception if any critical
    quality check fails.
    """

    logger.info("Starting data quality checks...")

    checks = {
        "NULL required fields": check_null_values(),
        "Invalid availability": check_invalid_availability(),
        "Invalid packet loss": check_invalid_packet_loss(),
        "Invalid latency": check_invalid_latency(),
        "Invalid signal strength": check_invalid_signal(),
        "Orphan measurements": check_orphan_measurements(),
    }

    failed_checks = []

    for check_name, count in checks.items():

        if count == 0:
            logger.info(f"PASS | {check_name}")

        else:
            logger.error(
                f"FAIL | {check_name} | "
                f"{count} bad records"
            )

            failed_checks.append(
                (check_name, count)
            )

    if failed_checks:

        message = "\n".join(
            f"- {name}: {count}"
            for name, count in failed_checks
        )

        raise ValueError(
            "Data quality checks failed:\n"
            + message
        )

    logger.info("All data quality checks passed.")


if __name__ == "__main__":
    run_quality_checks()
