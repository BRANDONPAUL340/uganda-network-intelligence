import csv
from datetime import datetime
from pathlib import Path

from sqlalchemy import text

from src.database import engine
from src.logger import get_logger
from src.data_quality.measurements import validate_record  # 🔑 Connective Link

# Initialize module-level logger instance
logger = get_logger(__name__)

# Landing path for incoming raw network file packets
SOURCE_FILE = Path("data/bronze/network_measurements.csv")


def read_measurements():
    """
    Safely opens and extracts raw dictionary records from the landing file.
    """
    logger.info(f"Reading measurement source | file={SOURCE_FILE}")

    if not SOURCE_FILE.exists():
        raise FileNotFoundError(f"Source file not found at landing path: {SOURCE_FILE}")

    with SOURCE_FILE.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        records = list(reader)

    logger.info(f"Source records read | records={len(records)}")
    return records


def create_source_record_id(record):
    """
    Generates a deterministic natural composite string key identifier.
    """
    return (
        f"{record['equipment_id'].strip()}_"
        f"{record['site_id'].strip()}_"
        f"{record['measured_at'].strip()}"
    )


def insert_measurements(records):
    """
    Validates rows via the comprehensive data quality engine before writing to staging.
    Trips an immediate circuit breaker if anomalies are caught.
    """
    sql = """
    INSERT INTO measurements (
        equipment_id, site_id, measured_at, traffic_mb, latency_ms,
        packet_loss_pct, signal_strength_dbm, availability_pct, source_record_id
    )
    VALUES (
        :equipment_id, :site_id, :measured_at, :traffic_mb, :latency_ms,
        :packet_loss_pct, :signal_strength_dbm, :availability_pct, :source_record_id
    )
    ON CONFLICT (source_record_id) DO NOTHING;
    """

    inserted = 0

    with engine.begin() as connection:
        for record in records:
            # 🛡️ Data Quality Firewall Gateway Rule Interception
            checks = validate_record(record)
            if not all(check["passed"] for check in checks):
                failed_checks = [c for check in checks if not check["passed"]]
                raise ValueError(f"Data quality validation failed: {failed_checks}")

            result = connection.execute(
                text(sql),
                {
                    "equipment_id": int(record["equipment_id"]),
                    "site_id": int(record["site_id"]),
                    "measured_at": datetime.strptime(record["measured_at"].strip(), "%Y-%m-%d %H:%M:%S"),
                    "traffic_mb": float(record["traffic_mb"]),
                    "latency_ms": float(record["latency_ms"]),
                    "packet_loss_pct": float(record["packet_loss_pct"]),
                    "signal_strength_dbm": float(record["signal_strength_dbm"]),
                    "availability_pct": float(record["availability_pct"]),
                    "source_record_id": create_source_record_id(record),
                }
            )
            inserted += result.rowcount

    logger.info(f"Measurements inserted | records={inserted}")
    return inserted


def run_ingestion():
    """
    Unified ingestion runner module entry point.
    """
    logger.info("--- INGESTION LAYER ---")

    records = read_measurements()
    inserted = insert_measurements(records)
    skipped = len(records) - inserted

    logger.info(
        f"Ingestion completed | source_records={len(records)} | "
        f"inserted_records={inserted} | skipped_records={skipped}"
    )

    return {
        "source_records": len(records),
        "inserted_records": inserted,
        "skipped_records": skipped,
    }


if __name__ == "__main__":
    run_ingestion()
