from sqlalchemy import text
from src.database import engine
from src.logger import get_logger

# Initialize package-level logger instance
logger = get_logger(__name__)


def get_count(sql):
    """Execute a COUNT query and return the result scalar integer value."""
    with engine.begin() as connection:
        return connection.execute(text(sql)).scalar()


def save_quality_result(
    run_id,
    table_name,
    check_name,
    status,
    records_checked,
    records_failed,
    error_message=None,
):
    """Persist one comprehensive quality-gate check result into the audit registry."""
    failure_rate = 0.0
    if records_checked and records_checked > 0:
        failure_rate = (records_failed / records_checked) * 100.0

    sql = """
    INSERT INTO data_quality_results (
        run_id,
        table_name,
        check_name,
        check_type,
        status,
        records_checked,
        records_failed,
        failure_rate_pct,
        details,
        error_message
    )
    VALUES (
        :run_id,
        :table_name,
        :check_name,
        'CRITICAL_GATE',
        :status,
        :records_checked,
        :records_failed,
        :failure_rate_pct,
        :details,
        :error_message
    );
    """
    details_str = (
        f"Critical contract rules for {check_name} pass perfectly."
        if status == "PASS"
        else f"Quality gate failure: {records_failed} anomalous rows found."
    )

    with engine.begin() as connection:
        connection.execute(
            text(sql),
            {
                "run_id": run_id,
                "table_name": table_name,
                "check_name": check_name,
                "status": status,
                "records_checked": records_checked,
                "records_failed": records_failed,
                "failure_rate_pct": failure_rate,
                "details": details_str,
                "error_message": error_message,
            },
        )


def build_quality_checks():
    """Return all 18 multi-table database quality assertions for the platform."""
    return [
        # =========================================================
        # SITES DIMENSION LAYER
        # =========================================================
        {
            "table": "sites",
            "name": "duplicate_sites",
            "sql": """
                SELECT COUNT(*)
                FROM (
                    SELECT site_name, district
                    FROM sites
                    GROUP BY site_name, district
                    HAVING COUNT(*) > 1
                ) duplicates;
            """,
        },
        {
            "table": "sites",
            "name": "invalid_latitude",
            "sql": """
                SELECT COUNT(*)
                FROM sites
                WHERE latitude IS NOT NULL AND (latitude < -90 OR latitude > 90);
            """,
        },
        {
            "table": "sites",
            "name": "invalid_longitude",
            "sql": """
                SELECT COUNT(*)
                FROM sites
                WHERE longitude IS NOT NULL AND (longitude < -180 OR longitude > 180);
            """,
        },
        {
            "table": "sites",
            "name": "missing_site_name",
            "sql": """
                SELECT COUNT(*)
                FROM sites
                WHERE site_name IS NULL OR TRIM(site_name) = '';
            """,
        },

        # =========================================================
        # EQUIPMENT DIMENSION LAYER
        # =========================================================
        {
            "table": "equipment",
            "name": "orphan_equipment_sites",
            "sql": """
                SELECT COUNT(*)
                FROM equipment e
                LEFT JOIN sites s ON e.site_id = s.site_id
                WHERE s.site_id IS NULL;
            """,
        },
        {
            "table": "equipment",
            "name": "missing_equipment_type",
            "sql": """
                SELECT COUNT(*)
                FROM equipment
                WHERE equipment_type IS NULL OR TRIM(equipment_type) = '';
            """,
        },
        {
            "table": "equipment",
            "name": "future_installation_date",
            "sql": """
                SELECT COUNT(*)
                FROM equipment
                WHERE installation_date > CURRENT_DATE;
            """,
        },

        # =========================================================
        # MEASUREMENTS TIME-SERIES FACT LAYER
        # =========================================================
        {
            "table": "measurements",
            "name": "negative_traffic",
            "sql": "SELECT COUNT(*) FROM measurements WHERE traffic_mb < 0;",
        },
        {
            "table": "measurements",
            "name": "negative_latency",
            "sql": "SELECT COUNT(*) FROM measurements WHERE latency_ms < 0;",
        },
        {
            "table": "measurements",
            "name": "invalid_packet_loss",
            "sql": "SELECT COUNT(*) FROM measurements WHERE packet_loss_pct < 0 OR packet_loss_pct > 100;",
        },
        {
            "table": "measurements",
            "name": "invalid_availability",
            "sql": "SELECT COUNT(*) FROM measurements WHERE availability_pct < 0 OR availability_pct > 100;",
        },
        {
            "table": "measurements",
            "name": "orphan_measurement_sites",
            "sql": """
                SELECT COUNT(*)
                FROM measurements m
                LEFT JOIN sites s ON m.site_id = s.site_id
                WHERE s.site_id IS NULL;
            """,
        },
        {
            "table": "measurements",
            "name": "orphan_measurement_equipment",
            "sql": """
                SELECT COUNT(*)
                FROM measurements m
                LEFT JOIN equipment e ON m.equipment_id = e.equipment_id
                WHERE e.equipment_id IS NULL;
            """,
        },

        # =========================================================
        # INCIDENTS LOG LAYER
        # =========================================================
        {
            "table": "incidents",
            "name": "orphan_incident_sites",
            "sql": """
                SELECT COUNT(*)
                FROM incidents i
                LEFT JOIN sites s ON i.site_id = s.site_id
                WHERE s.site_id IS NULL;
            """,
        },
        {
            "table": "incidents",
            "name": "orphan_incident_equipment",
            "sql": """
                SELECT COUNT(*)
                FROM incidents i
                LEFT JOIN equipment e ON i.equipment_id = e.equipment_id
                WHERE i.equipment_id IS NOT NULL AND e.equipment_id IS NULL;
            """,
        },
        {
            "table": "incidents",
            "name": "invalid_incident_times",
            "sql": "SELECT COUNT(*) FROM incidents WHERE end_time IS NOT NULL AND end_time < start_time;",
        },
        {
            "table": "incidents",
            "name": "missing_incident_type",
            "sql": "SELECT COUNT(*) FROM incidents WHERE incident_type IS NULL OR TRIM(incident_type) = '';",
        },
        {
            "table": "incidents",
            "name": "missing_severity",
            "sql": "SELECT COUNT(*) FROM incidents WHERE severity IS NULL OR TRIM(severity) = '';",
        },
    ]


def run_quality_gate(run_id):
    """
    Evaluates global multi-table checks and acts as a strict circuit breaker.
    Raises a RuntimeError immediately if any non-negotiable contract checks fail.
    """
    print("\n--- DATA QUALITY GATE ---")
    logger.info(f"Initializing multi-table Data Quality Gate firewall for run_id={run_id}")

    checks = build_quality_checks()
    quality_passed = True

    for check in checks:
        table_name = check["table"]
        check_name = check["name"]

        failed_records = get_count(check["sql"])
        records_checked = get_count(f"SELECT COUNT(*) FROM {table_name};")

        if failed_records == 0:
            status = "PASS"
            print(f"PASS: {check_name}")
        else:
            status = "FAIL"
            quality_passed = False
            print(f"FAIL: {check_name} ({failed_records} anomalous records found inside {table_name})")
            logger.warning(f"⚠️ Critical Gate Violation! Check: {check_name} | Failures: {failed_records}")

        # 🚀 Persist each outcome into our unified relational database ledger
        save_quality_result(
            run_id=run_id,
            table_name=table_name,
            check_name=check_name,
            status=status,
            records_checked=records_checked,
            records_failed=failed_records,
        )

    if not quality_passed:
        raise RuntimeError(
            "Data quality gate failed. Global table anomalies caught. "
            "Gold transformations will not run."
        )

    print("DATA QUALITY GATE PASSED.")
    logger.info(f"Global Data Quality Gate successfully passed for run_id={run_id}")
    return True
