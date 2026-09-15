import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Enforce explicit header schemas to trap formatting deviations at the perimeter
REQUIRED_COLUMNS = {
    "measurement_id",
    "site_id",
    "equipment_id",
    "measurement_date",
    "traffic_mb",
    "latency_ms",
    "packet_loss_pct",
    "signal_strength_dbm",
    "availability_pct",
}


def read_measurements_csv(file_path):
    """
    Parses an incoming telemetry CSV file into structured record lists.
    Validates column headers against strict system criteria.
    """
    file_path = Path(file_path)
    logger.info(f"Opening inbound telemetry dataset: [{file_path.name}]")

    if not file_path.exists():
        raise FileNotFoundError(f"Target CSV file not found on disk: {file_path}")

    with file_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(f"Aborting ingest: CSV file has no headers: {file_path.name}")

        # Check for structural schema drift using set operations
        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing_columns:
            error_msg = f"CSV schema contract breach. Missing columns: {sorted(missing_columns)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        records = list(reader)
        logger.info(f"Successfully unpacked {len(records)} records from {file_path.name}")
        return records
