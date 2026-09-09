from sqlalchemy import text
from src.database import engine
from src.logger import get_logger
from src.data_quality.severity import determine_severity # 🔑 Newly Imported Helper!

logger = get_logger(__name__)


def build_quality_checks():
    """
    Returns the complete portfolio of 18 declarative multi-table 
    data quality validation checks.
    """
    return [
        {"table": "sites", "name": "duplicate_sites", "sql": "SELECT COUNT(*) FROM sites GROUP BY site_name, district HAVING COUNT(*) > 1"},
        {"table": "sites", "name": "invalid_latitude", "sql": "SELECT COUNT(*) FROM sites WHERE latitude < -1.5 OR latitude > 4.5"},
        {"table": "sites", "name": "invalid_longitude", "sql": "SELECT COUNT(*) FROM sites WHERE longitude < 29.5 OR longitude > 35.5"},
        {"table": "sites", "name": "missing_site_name", "sql": "SELECT COUNT(*) FROM sites WHERE site_name IS NULL OR site_name = ''"},
        {"table": "equipment", "name": "orphan_equipment_sites", "sql": "SELECT COUNT(*) FROM equipment e LEFT JOIN sites s ON e.site_id = s.site_id WHERE s.site_id IS NULL"},
        {"table": "equipment", "name": "missing_equipment_type", "sql": "SELECT COUNT(*) FROM equipment WHERE equipment_type IS NULL OR equipment_type = ''"},
        {"table": "equipment", "name": "future_installation_date", "sql": "SELECT COUNT(*) FROM equipment WHERE installation_date > CURRENT_DATE"},
        {"table": "measurements", "name": "negative_traffic", "sql": "SELECT COUNT(*) FROM measurements WHERE traffic_mb < 0"},
        {"table": "measurements", "name": "negative_latency", "sql": "SELECT COUNT(*) FROM measurements WHERE latency_ms < 0"},
        {"table": "measurements", "name": "invalid_packet_loss", "sql": "SELECT COUNT(*) FROM measurements WHERE packet_loss_pct < 0 OR packet_loss_pct > 100"},
        {"table": "measurements", "name": "invalid_availability", "sql": "SELECT COUNT(*) FROM measurements WHERE availability_pct < 0 OR availability_pct > 100"},
        {"table": "measurements", "name": "orphan_measurement_sites", "sql": "SELECT COUNT(*) FROM measurements m LEFT JOIN sites s ON m.site_id = s.site_id WHERE s.site_id IS NULL"},
        {"table": "measurements", "name": "orphan_measurement_equipment", "sql": "SELECT COUNT(*) FROM measurements m LEFT JOIN equipment e ON m.equipment_id = e.equipment_id WHERE e.equipment_id IS NULL"},
        {"table": "incidents", "name": "orphan_incident_sites", "sql": "SELECT COUNT(*) FROM incidents i LEFT JOIN sites s ON i.site_id = s.site_id WHERE s.site_id IS NULL"},
        {"table": "incidents", "name": "orphan_incident_equipment", "sql": "SELECT COUNT(*) FROM incidents i LEFT JOIN equipment e ON i.equipment_id = e.equipment_id WHERE e.equipment_id IS NULL"},
        {"table": "incidents", "name": "invalid_incident_times", "sql": "SELECT COUNT(*) FROM incidents WHERE end_time IS NOT NULL AND end_time < start_time"},
        {"table": "incidents", "name": "missing_incident_type", "sql": "SELECT COUNT(*) FROM incidents WHERE incident_type IS NULL OR incident_type = ''"},
        {"table": "incidents", "name": "missing_severity", "sql": "SELECT COUNT(*) FROM incidents WHERE severity IS NULL OR severity = ''"}
    ]


def run_quality_gate(run_id):
    """
    Executes all declarative data quality checks for the given run_id.
    Logs each result to the database and returns a programmatic summary dictionary.
    """
    print("\n--- DATA QUALITY GATE ---")
    logger.info(f"Starting 18-point data quality checks for run_id={run_id}")
    
    checks = build_quality_checks()
    total_checks = len(checks)
    passed_checks = 0
    failed_checks = 0
    total_failed_records = 0
    critical_breaches_found = 0

    insert_sql = """
    INSERT INTO data_quality_results (
        run_id, table_name, check_name, status, records_checked, records_failed, check_type, severity
    ) VALUES (
        :run_id, :table_name, :check_name, :status, :records_checked, :records_failed, 'VALIDITY', :severity
    );
    """

    with engine.begin() as connection:
        for check in checks:
            # Determine validation sample scope size
            scope_sql = f"SELECT COUNT(*) FROM {check['table']};"
            records_checked = connection.execute(text(scope_sql)).scalar() or 0
            
            # Execute violation validation query scanner
            failed_rows = connection.execute(text(check["sql"])).scalar() or 0
            status = "FAIL" if failed_rows > 0 else "PASS"
            
            # 🚀 Compute dynamic multi-tier severity using your centralized helper
            severity = determine_severity(check["name"], failed_rows)
            
            if status == "PASS":
                passed_checks += 1
            else:
                failed_checks += 1
                total_failed_records += failed_rows
                if severity == "CRITICAL":
                    critical_breaches_found += 1

            print(f"{status}: {check['table']}.{check['name']} | Severity: {severity} ({failed_rows} records failed)")

            # Record footprint to database logs
            connection.execute(
                text(insert_sql),
                {
                    "run_id": run_id,
                    "table_name": check["table"],
                    "check_name": check["name"],
                    "status": status,
                    "records_checked": records_checked,
                    "records_failed": failed_rows,
                    "severity": severity
                }
            )

    logger.info(f"Quality gate complete | total={total_checks} | passed={passed_checks} | failed={failed_checks}")
    
    return {
        "checks": total_checks,
        "passed": passed_checks,
        "failed": failed_checks,
        "failed_records": total_failed_records,
        "critical_failed": critical_breaches_found
    }
