import logging
from sqlalchemy import text
from src.database import engine

logger = logging.getLogger(__name__)

# 🔒 Required Columns Data Contract
REQUIRED_COLUMNS = {
    "sites": {
        "site_id",
        "site_name",
        "region",
        "district",
    },
    "equipment": {
        "equipment_id",
        "site_id",
        "equipment_type",
        "manufacturer",
        "model",
    },
    "measurements": {
        "measurement_id",
        "site_id",
        "equipment_id",
        "measured_at",
        "traffic_mb",
        "latency_ms",
        "packet_loss_pct",
        "signal_strength_dbm",
        "availability_pct",
    },
    "incidents": {
        "incident_id",
        "site_id",
        "equipment_id",
        "start_time",
        "incident_type",
        "severity",
        "description",
    },
}

# 🔒 Allowed Data Types Data Contract
EXPECTED_TYPES = {
    "measurements": {
        "measurement_id": {"integer", "bigint", "smallint"},
        "site_id": {"integer", "bigint", "smallint"},
        "equipment_id": {"integer", "bigint", "smallint"},
        "latency_ms": {"numeric", "double precision", "real"},
        "packet_loss_pct": {"numeric", "double precision", "real"},
        "availability_pct": {"numeric", "double precision", "real"},
    }
}


def get_table_columns(table_name):
    """Queries the database to fetch actual column names on disk."""
    query = text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = :table_name
        ORDER BY ordinal_position;
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {"table_name": table_name},
        ).fetchall()

    return {row[0] for row in rows}


def get_column_types(table_name):
    """Queries the database to fetch column names and their physical data types."""
    query = text("""
        SELECT
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = :table_name;
    """)

    with engine.connect() as connection:
        rows = connection.execute(
            query,
            {"table_name": table_name},
        ).fetchall()

    return {row[0]: row[1] for row in rows}


def validate_required_columns():
    """Identifies missing tables or fields across the active data layer."""
    errors = []

    for table_name, required_columns in REQUIRED_COLUMNS.items():
        actual_columns = get_table_columns(table_name)

        if not actual_columns:
            errors.append(f"Missing table: {table_name}")
            continue

        missing_columns = required_columns - actual_columns

        for column in sorted(missing_columns):
            errors.append(f"Missing column: {table_name}.{column}")

    return errors


def validate_column_types():
    """Identifies columns whose types violate the allowed data types contract."""
    errors = []

    for table_name, columns in EXPECTED_TYPES.items():
        actual_types = get_column_types(table_name)

        for column_name, allowed_types in columns.items():
            actual_type = actual_types.get(column_name)

            if actual_type is None:
                continue

            if actual_type not in allowed_types:
                errors.append(
                    f"Invalid type: {table_name}.{column_name} "
                    f"is {actual_type}, expected one of {sorted(allowed_types)}"
                )

    return errors


def validate_schema():
    """Executes the complete structure-and-type contract firewall pass."""
    logger.info("Executing pre-flight schema contract validations...")
    errors = []

    errors.extend(validate_required_columns())
    errors.extend(validate_column_types())

    return {
        "passed": len(errors) == 0,
        "errors": errors,
    }
