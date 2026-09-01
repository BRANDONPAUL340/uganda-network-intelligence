from sqlalchemy import text

from src.database import engine
from src.logger import get_logger

# 🛠️ Hardened: Instantiating centralized module logger context name
logger = get_logger(__name__)


def record_quality_result(run_id, check_name, table_name, status, failed_records, details=None):
    sql = """
    INSERT INTO data_quality_results (run_id, check_name, table_name, status, failed_records, details)
    VALUES (:run_id, :check_name, :table_name, :status, :failed_records, :details);
    """
    with engine.begin() as connection:
        connection.execute(
            text(sql),
            {
                "run_id": run_id,
                "check_name": check_name,
                "table_name": table_name,
                "status": status,
                "failed_records": failed_records,
                "details": details,
            }
        )


def run_check(run_id, check_name, table_name, sql):
    with engine.begin() as connection:
        result = connection.execute(text(sql))
        failed_records = result.scalar() or 0

    status = "PASS" if failed_records == 0 else "FAIL"

    # Log individual scorecards straight to disk
    if status == "PASS":
        logger.info("Data quality check passed: %s | failures=%s", check_name, failed_records)
    else:
        logger.error("Data quality check failed: %s | failures=%s", check_name, failed_records)

    record_quality_result(
        run_id=run_id,
        check_name=check_name,
        table_name=table_name,
        status=status,
        failed_records=failed_records
    )

    return {"check_name": check_name, "status": status, "failed_records": failed_records}


def check_required_site_id(run_id):
    sql = "SELECT COUNT(*) FROM measurements WHERE site_id IS NULL;"
    return run_check(run_id, "required_site_id", "measurements", sql)


def check_required_equipment_id(run_id):
    sql = "SELECT COUNT(*) FROM measurements WHERE equipment_id IS NULL;"
    return run_check(run_id, "required_equipment_id", "measurements", sql)


def check_valid_latency(run_id):
    sql = "SELECT COUNT(*) FROM measurements WHERE latency_ms < 0;"
    return run_check(run_id, "valid_latency", "measurements", sql)


def check_valid_packet_loss(run_id):
    sql = "SELECT COUNT(*) FROM measurements WHERE packet_loss_pct < 0 OR packet_loss_pct > 100;"
    return run_check(run_id, "valid_packet_loss", "measurements", sql)


def check_valid_availability(run_id):
    sql = "SELECT COUNT(*) FROM measurements WHERE availability_pct < 0 OR availability_pct > 100;"
    return run_check(run_id, "valid_availability", "measurements", sql)


def check_duplicate_measurements(run_id):
    sql = """
    SELECT COUNT(*) FROM (
        SELECT measurement_id FROM measurements GROUP BY measurement_id HAVING COUNT(*) > 1
    ) duplicates;
    """
    return run_check(run_id, "duplicate_measurements", "measurements", sql)


def check_orphan_measurements(run_id):
    sql = "SELECT COUNT(*) FROM measurements m LEFT JOIN sites s ON m.site_id = s.site_id WHERE s.site_id IS NULL;"
    return run_check(run_id, "orphan_measurements", "measurements", sql)


def check_orphan_equipment(run_id):
    sql = "SELECT COUNT(*) FROM measurements m LEFT JOIN equipment e ON m.equipment_id = e.equipment_id WHERE e.equipment_id IS NULL;"
    return run_check(run_id, "orphan_equipment", "measurements", sql)


def check_incident_dates(run_id):
    sql = "SELECT COUNT(*) FROM incidents WHERE end_time IS NOT NULL AND end_time < start_time;"
    return run_check(run_id, "valid_incident_dates", "incidents", sql)


def run_data_quality(run_id):
    logger.info("--- DATA QUALITY ---")

    results = []
    results.append(check_required_site_id(run_id))
    results.append(check_required_equipment_id(run_id))
    results.append(check_valid_latency(run_id))
    results.append(check_valid_packet_loss(run_id))
    results.append(check_valid_availability(run_id))
    results.append(check_duplicate_measurements(run_id))
    results.append(check_orphan_measurements(run_id))
    results.append(check_orphan_equipment(run_id))
    results.append(check_incident_dates(run_id))

    # 🛠️ Fixed: Indentation perfectly aligned to exactly 4 spaces
    failed_checks = sum(1 for result in results if result["status"] == "FAIL")

    # 🔑 Parameterized: Unified summary layout matches our standard framework tracking rules
    logger.info(
        "Data quality completed. checks=%s failed=%s",
        len(results),
        failed_checks
    )

    return {"checks_run": len(results), "failed_checks": failed_checks, "results": results}


if __name__ == "__main__":
    run_data_quality(None)
