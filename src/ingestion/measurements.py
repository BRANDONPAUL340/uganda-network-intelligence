import csv
from datetime import datetime
from pathlib import Path

from sqlalchemy import text

from src.database import engine
from src.logger import get_logger
from src.data_quality.measurements import validate_record, get_validation_failure
from src.data_quality.quarantine import reject_measurement

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
    # Defensive handle: if equipment_id or site_id are completely missing, fallback gracefully
    eq_id = str(record.get("equipment_id", "")).strip()
    st_id = str(record.get("site_id", "")).strip()
    ts = str(record.get("measured_at", "")).strip()
    return f"{eq_id}_{st_id}_{ts}"


def insert_measurements(records):
    """
    Validates, processes, and branches rows at the perimeter interface layer.
    Routes clean records downstream while flushing anomalous rows straight to quarantine.
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
    rejected = 0

    with engine.begin() as connection:
        for record in records:
            # 🛡️ Data Quality Firewall Gateway Rule Interception
            checks = validate_record(record)
            reason = get_validation_failure(checks)

            # Generate record ID early so it's traceable in logs/quarantine
            record["source_record_id"] = create_source_record_id(record)

            if reason:
                # 🛑 ANOMALOUS PATHWAY BRANCH: Load to quarantine, increment tracker, and skip insert
                reject_measurement(
                    record=record,
                    reason=reason,
                    source_file="network_measurements.csv"
                )
                rejected += 1
                continue

            # ✅ CLEAN PATHWAY BRANCH: Typecast metrics values and flush downstream
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
                    "source_record_id": record["source_record_id"]
                }
            )
            inserted += result.rowcount

    return inserted, rejected


def run_ingestion():
    """
    Unified ingestion runner module entry point.
    """
    logger.info("--- INGESTION LAYER ---")

    records = read_measurements()
    source_records = len(records)
    
    inserted, rejected = insert_measurements(records)

    logger.info(
        "Ingestion completed | "
        f"source_records={source_records} | "
        f"inserted_records={inserted} | "
        f"rejected_records={rejected}"
    )

    return {
        "source_records": source_records,
        "inserted_records": inserted,
        "rejected_records": rejected
    }


if __name__ == "__main__":
    run_ingestion()
