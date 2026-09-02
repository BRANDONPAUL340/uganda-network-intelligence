from sqlalchemy import text

from src.database import engine
from src.logger import get_logger

# 🛠️ Hardened: Instantiating centralized module logger context name
logger = get_logger(__name__)


def check_sites_for_nulls():
    sql = """
    SELECT COUNT(*)
    FROM sites
    WHERE site_name IS NULL
       OR region IS NULL
       OR district IS NULL
       OR site_type IS NULL
       OR status IS NULL;
    """
    with engine.connect() as connection:
        result = connection.execute(text(sql))
        return result.scalar() == 0


def check_duplicate_sites():
    sql = """
    SELECT COUNT(*)
    FROM (
        SELECT site_name, district
        FROM sites
        GROUP BY site_name, district
        HAVING COUNT(*) > 1
    ) duplicates;
    """
    with engine.connect() as connection:
        result = connection.execute(text(sql))
        return result.scalar() == 0


def check_measurement_ranges():
    sql = """
    SELECT COUNT(*)
    FROM measurements
    WHERE
        (traffic_mb IS NOT NULL AND traffic_mb < 0)
        OR
        (latency_ms IS NOT NULL AND latency_ms < 0)
        OR
        (
            packet_loss_pct IS NOT NULL
            AND packet_loss_pct NOT BETWEEN 0 AND 100
        )
        OR
        (
            availability_pct IS NOT NULL
            AND availability_pct NOT BETWEEN 0 AND 100
        );
    """
    with engine.connect() as connection:
        result = connection.execute(text(sql))
        return result.scalar() == 0


def check_orphan_equipment():
    sql = """
    SELECT COUNT(*)
    FROM equipment e
    LEFT JOIN sites s
        ON e.site_id = s.site_id
    WHERE s.site_id IS NULL;
    """
    with engine.connect() as connection:
        result = connection.execute(text(sql))
        return result.scalar() == 0


def check_orphan_measurements():
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

    with engine.connect() as connection:
        result = connection.execute(text(sql))
        return result.scalar() == 0


def check_incident_dates():
    sql = """
    SELECT COUNT(*)
    FROM incidents
    WHERE end_time IS NOT NULL
      AND end_time < start_time;
    """
    with engine.connect() as connection:
        result = connection.execute(text(sql))
        return result.scalar() == 0


def run_data_quality_checks():
    logger.info("🎬 Starting comprehensive data quality validation checks...")

    checks = {
        "sites_not_null": check_sites_for_nulls(),
        "duplicate_sites": check_duplicate_sites(),
        "measurement_ranges": check_measurement_ranges(),
        "orphan_equipment": check_orphan_equipment(),
        "orphan_measurements": check_orphan_measurements(),
        "incident_dates": check_incident_dates(),
    }

    print("\n--- DATA QUALITY RESULTS ---")

    all_passed = True

    for check_name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"{check_name}: {status}")

        if passed:
            logger.info("✅ PASS | %s", check_name)
        else:
            logger.error("❌ FAIL | %s | Data quality issue caught!", check_name)
            all_passed = False

    if all_passed:
        logger.info("🎉 All data-quality checks passed cleanly.")
    else:
        logger.warning("⚠️ Critical data governance anomalies flagged inside checks framework.")

    # 🔑 Connected: Yields the structural dictionary payload to prevent script crashes
    return {
        "passed": all_passed,
        "checks": checks,
    }


if __name__ == "__main__":
    passed_dict = run_data_quality_checks()
    if passed_dict["passed"]:
        print("\nAll data-quality checks passed.")
    else:
        print("\nData-quality checks failed.")
