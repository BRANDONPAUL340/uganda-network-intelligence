from datetime import datetime
from sqlalchemy import text
from src.database import engine
from src.logger import get_logger

# Initialize module-level logger instance
logger = get_logger(__name__)


def check_required_fields(record):
    """Asserts the physical presence of all required attributes."""
    required_fields = [
        "equipment_id",
        "site_id",
        "measured_at",
        "traffic_mb",
        "latency_ms",
        "packet_loss_pct",
        "signal_strength_dbm",
        "availability_pct",
    ]

    missing = [
        field
        for field in required_fields
        if not record.get(field) or str(record.get(field)).strip() == ""
    ]

    if missing:
        return {
            "passed": False,
            "check": "required_fields",
            "message": f"Missing fields: {', '.join(missing)}",
        }

    return {
        "passed": True,
        "check": "required_fields",
        "message": "All required fields present",
    }


def check_numeric_fields(record):
    """Verifies that raw text strings can parse cleanly into numbers."""
    numeric_fields = [
        "traffic_mb",
        "latency_ms",
        "packet_loss_pct",
        "signal_strength_dbm",
        "availability_pct",
    ]

    try:
        for field in numeric_fields:
            float(record[field])
    except (TypeError, ValueError):
        return {
            "passed": False,
            "check": "numeric_fields",
            "message": "Invalid numeric value",
        }

    return {
        "passed": True,
        "check": "numeric_fields",
        "message": "Numeric values valid",
    }


def check_metric_ranges(record):
    """Enforces boundaries reflecting physical network constraints."""
    try:
        traffic = float(record["traffic_mb"])
        latency = float(record["latency_ms"])
        packet_loss = float(record["packet_loss_pct"])
        availability = float(record["availability_pct"])
    except (TypeError, ValueError):
        return {
            "passed": False,
            "check": "metric_ranges",
            "message": "Range check bypassed: Invalid numeric types",
        }

    if traffic < 0:
        return {
            "passed": False,
            "check": "metric_ranges",
            "message": "Traffic cannot be negative",
        }

    if latency < 0:
        return {
            "passed": False,
            "check": "metric_ranges",
            "message": "Latency cannot be negative",
        }

    if not 0 <= packet_loss <= 100:
        return {
            "passed": False,
            "check": "metric_ranges",
            "message": "Packet loss must be between 0 and 100",
        }

    if not 0 <= availability <= 100:
        return {
            "passed": False,
            "check": "metric_ranges",
            "message": "Availability must be between 0 and 100",
        }

    return {
        "passed": True,
        "check": "metric_ranges",
        "message": "Network metric ranges valid",
    }


def check_timestamp(record):
    """Validates chronology string mask adherence."""
    try:
        datetime.strptime(record["measured_at"].strip(), "%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        return {
            "passed": False,
            "check": "timestamp",
            "message": "Invalid measurement timestamp",
        }

    return {
        "passed": True,
        "check": "timestamp",
        "message": "Timestamp valid",
    }


def check_reference_data(record):
    """Queries relational tables to intercept invalid site or equipment reference mappings."""
    sql = """
    SELECT
        EXISTS (
            SELECT 1
            FROM sites
            WHERE site_id = :site_id
        ) AS site_exists,

        EXISTS (
            SELECT 1
            FROM equipment
            WHERE equipment_id = :equipment_id
        ) AS equipment_exists;
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text(sql),
                {
                    "site_id": int(record["site_id"]),
                    "equipment_id": int(record["equipment_id"]),
                },
            ).mappings().one()
    except (TypeError, ValueError):
        return {
            "passed": False,
            "check": "reference_data",
            "message": "Invalid site_id or equipment_id data type supplied",
        }

    if not result["site_exists"]:
        return {
            "passed": False,
            "check": "site_reference",
            "message": f"Site {record['site_id']} does not exist",
        }

    if not result["equipment_exists"]:
        return {
            "passed": False,
            "check": "equipment_reference",
            "message": f"Equipment {record['equipment_id']} does not exist",
        }

    return {
        "passed": True,
        "check": "reference_data",
        "message": "Site and equipment references valid",
    }


def validate_record(record):
    """Orchestrates sequential validation steps for a record row."""
    checks = [check_required_fields(record)]
    if not checks[-1]["passed"]:
        return checks

    checks.append(check_numeric_fields(record))
    if not checks[-1]["passed"]:
        return checks

    checks.append(check_metric_ranges(record))
    if not checks[-1]["passed"]:
        return checks

    checks.append(check_timestamp(record))
    if not checks[-1]["passed"]:
        return checks

    checks.append(check_reference_data(record))
    return checks


def get_validation_failure(checks):
    """Scans checks results and returns the first failure message text caught."""
    for check in checks:
        if not check["passed"]:
            return check["message"]
    return None


def summarize_quality(records):
    """Evaluates an array of records and outputs a quality scorecard metadata map."""
    total = len(records)
    passed = 0
    failed = 0
    failures = []

    for record in records:
        checks = validate_record(record)
        record_passed = all(check["passed"] for check in checks)

        if record_passed:
            passed += 1
        else:
            failed += 1
            failures.append({
                "record": record,
                "checks": checks,
            })

    summary = {
        "total_records": total,
        "passed_records": passed,
        "failed_records": failed,
        "quality_rate": (passed / total * 100 if total > 0 else 0),
        "failures": failures,
    }

    logger.info(
        f"Data quality summary | total={total} | passed={passed} | "
        f"failed={failed} | quality_rate={summary['quality_rate']:.2f}%"
    )

    return summary


if __name__ == "__main__":
    from src.ingestion.measurements import read_measurements

    try:
        raw_records = read_measurements()
        quality_summary = summarize_quality(raw_records)

        print("\nDATA QUALITY SUMMARY")
        print("=" * 40)
        print(f"Total records:  {quality_summary['total_records']}")
        print(f"Passed records: {quality_summary['passed_records']}")
        print(f"Failed records: {quality_summary['failed_records']}")
        print(f"Quality rate:   {quality_summary['quality_rate']:.2f}%")
    except Exception as err:
        print(f"\nExecution crash: {err}")
