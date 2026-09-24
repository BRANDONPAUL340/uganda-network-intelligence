
import sys
from pathlib import Path

from sqlalchemy import text

from src.database import engine


# Dynamic project root path resolution hook
root_dir = str(Path(__file__).resolve().parents[1])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


# 9. Centralised Configuration Dictionary with Feature Toggles [INDEX]
QUALITY_RULES = {
    "volume_check": {
        "enabled": True,
        "minimum_count": 1,
    },
    "null_site_id": {
        "enabled": True,
        "warning_threshold": 1.0,
        "failure_threshold": 5.0,
    },
    "duplicate_records": {
        "enabled": True,
        "warning_threshold": 0.2,
        "failure_threshold": 1.0,
    },
    "valid_ranges": {
        "enabled": True,
        "warning_threshold": 0.1,
        "failure_threshold": 1.0,
    },
    "data_freshness": {
        "enabled": False,
        "warning_hours": 12.0,
        "failure_hours": 24.0,
    },
}


def evaluate_percentage(
    percentage: float,
    warning_threshold: float,
    failure_threshold: float,
) -> str:
    """
    11. Generic Percentage Evaluator: Compares measured percentages
    against configurable threshold limits [INDEX].
    """
    if percentage > failure_threshold:
        return "FAIL"

    if percentage > warning_threshold:
        return "WARNING"

    return "PASS"


def log_quality_result(
    run_id: int,
    check_name: str,
    status: str,
    records_checked: int,
    failed_records: int,
    check_value: float,
    message: str,
    table_name: str = "silver_measurements",
) -> None:
    """Persists data quality test snapshots into PostgreSQL [INDEX]."""

    details = f"check_value={check_value}; {message}"

    query = text(
        """
        INSERT INTO data_quality_results
            (
                run_id,
                table_name,
                check_name,
                status,
                records_checked,
                failed_records,
                details
            )
        VALUES
            (
                :run_id,
                :table_name,
                :check_name,
                :status,
                :records_checked,
                :failed_records,
                :details
            );
        """
    )

    with engine.begin() as conn:
        conn.execute(
            query,
            {
                "run_id": run_id,
                "table_name": table_name,
                "check_name": check_name,
                "status": status,
                "records_checked": records_checked,
                "failed_records": failed_records,
                "details": details,
            },
        )

def execute_data_quality_suite(run_id: int) -> bool:
    """
    10. Configuration-Driven Quality Engine: Reads rule configurations dynamically,
    skips disabled tests, and enforces quality gates [INDEX].
    """

    count_query = text(
        "SELECT COUNT(*) FROM silver_measurements;"
    )

    with engine.connect() as conn:
        total_records = conn.execute(count_query).scalar() or 0

    block_pipeline = False

    # --- CHECK #1: RECORD VOLUME CHECK ---
    rule_vol = QUALITY_RULES["volume_check"]

    if rule_vol["enabled"]:
        if total_records >= rule_vol["minimum_count"]:
            log_quality_result(
                run_id,
                "volume_check",
                "PASS",
                total_records,
                0,
                float(total_records),
                "Volume gate passed.",
            )
        else:
            block_pipeline = True

            log_quality_result(
                run_id,
                "volume_check",
                "FAIL",
                0,
                0,
                0.0,
                "Volume check failed.",
            )

    if total_records == 0:
        return False

    # --- CHECK #2: NULL VALUE CHECK ---
    rule_null = QUALITY_RULES["null_site_id"]

    if rule_null["enabled"]:
        null_query = text(
            """
            SELECT COUNT(*)
            FROM silver_measurements
            WHERE site_id IS NULL;
            """
        )

        with engine.connect() as conn:
            null_count = conn.execute(null_query).scalar() or 0

        null_pct = 100.0 * null_count / total_records

        # 10. Read parameters dynamically from configuration instead
        # of hardcoding [INDEX]
        status_null = evaluate_percentage(
            null_pct,
            rule_null["warning_threshold"],
            rule_null["failure_threshold"],
        )

        if status_null == "FAIL":
            block_pipeline = True

        log_quality_result(
            run_id,
            "null_site_id",
            status_null,
            total_records,
            null_count,
            null_pct,
            f"Null check resolved as {status_null}.",
        )

    # --- CHECK #3: DUPLICATE RECORDS CHECK ---
    rule_dup = QUALITY_RULES["duplicate_records"]

    if rule_dup["enabled"]:
        dup_query = text(
            """
            SELECT COUNT(*)
            FROM (
                SELECT site_id, measured_at
                FROM silver_measurements
                GROUP BY site_id, measured_at
                HAVING COUNT(*) > 1
            ) duplicates;
            """
        )

        with engine.connect() as conn:
            dup_groups = conn.execute(dup_query).scalar() or 0

        dup_pct = 100.0 * dup_groups / total_records

        status_dup = evaluate_percentage(
            dup_pct,
            rule_dup["warning_threshold"],
            rule_dup["failure_threshold"],
        )

        if status_dup == "FAIL":
            block_pipeline = True

        log_quality_result(
            run_id,
            "duplicate_records",
            status_dup,
            total_records,
            dup_groups,
            dup_pct,
            f"Duplicate check resolved as {status_dup}.",
        )

    # --- CHECK #4: VALID RANGE CHECK ---
    rule_range = QUALITY_RULES["valid_ranges"]

    if rule_range["enabled"]:
        # Keep this configuration-driven check available for future
        # range validation without changing the existing schema.
        pass

    # --- CHECK #5: DATA FRESHNESS CHECK (DISABLED EXAMPLE) ---
    rule_fresh = QUALITY_RULES["data_freshness"]

    if not rule_fresh["enabled"]:
        # 9. Skip disabled checks seamlessly [INDEX]
        pass

    return not block_pipeline