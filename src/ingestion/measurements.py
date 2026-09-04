import csv
from datetime import datetime
from pathlib import Path

from sqlalchemy import text

from src.database import engine
from src.logger import get_logger
from src.validation.measurement_contract import validate_measurement  # 🔑 Connect Data Contract
from src.data_quality.quarantine import reject_measurement

# Initialize module-level logger instance
logger = get_logger(__name__)

# Landing path for incoming raw network file packets
SOURCE_FILE = Path("data/bronze/network_measurements.csv")


def read_measurements():
    """Safely opens and extracts raw dictionary records from the landing file."""
    logger.info(f"Reading measurement source | file={SOURCE_FILE}")

    if not SOURCE_FILE.exists():
        raise FileNotFoundError(f"Source file not found at landing path: {SOURCE_FILE}")

    with SOURCE_FILE.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        records = list(reader)

    logger.info(f"Source records read | records={len(records)}")
    return records


def create_source_record_id(record):
    """Generates a deterministic natural composite string key identifier."""
    eq_id = str(record.get("equipment_id", "")).strip()
    st_id = str(record.get("site_id", "")).strip()
    ts = str(record.get("measured_at", "")).strip()
    return f"{eq_id}_{st_id}_{ts}"


def get_processed_source_ids():
    """
    Queries the database staging ledger and returns a unique set of all 
    previously ingested natural record string key signatures.
    """
    sql = """
    SELECT source_record_id
    FROM measurements
    WHERE source_record_id IS NOT NULL;
    """
    with engine.begin() as connection:
        result = connection.execute(text(sql))
        return {row[0] for row in result}


def insert_measurements(records):
    """
    Validates, filters, and loads records incrementally against a strict data contract.
    Routes clean records downstream while flushing contract violations straight to quarantine.
    """
    sql = """
    INSERT INTO measurements (
        source_record_id, equipment_id, site_id, measured_at, traffic_mb,
        latency_ms, packet_loss_pct, signal_strength_dbm, availability_pct
    )
    VALUES (
        :source_record_id, :equipment_id, :site_id, :measured_at, :traffic_mb,
        :latency_ms, :packet_loss_pct, :signal_strength_dbm, :availability_pct
    )
    ON CONFLICT (source_record_id) DO NOTHING;
    """

    inserted = 0
    rejected = 0
    skipped = 0

    # Fetch all historical signatures from database catalog
    processed_ids = get_processed_source_ids()

    with engine.begin() as connection:
        for record in records:
            # Generate deterministic token ID early for comparison checks
            source_record_id = create_source_record_id(record)
            record["source_record_id"] = source_record_id

            # 🛠️ 1. Change-Data Capture (CDC) Filter Bypass Guard
            if source_record_id in processed_ids:
                skipped += 1
                logger.info(f"Skipping already processed record | source_record_id={source_record_id}")
                continue

            # Parse a temporary record with proper datetime object to feed to the Data Contract engine
            temp_record = dict(record)
            try:
                temp_record["measured_at"] = datetime.strptime(str(record.get("measured_at")).strip(), "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                temp_record["measured_at"] = None  # Contract will catch malformed types cleanly

            # 🛠️ 2. Data Contract Rule Interception Firewall Gateway
            errors = validate_measurement(temp_record)

            if errors:
                # 🛑 CONTRACT VIOLATION BRANCH: Combine error list into a string, log to quarantine, and skip insert
                combined_reason = "; ".join(errors)
                reject_measurement(
                    record=record,
                    reason=combined_reason,
                    source_file="network_measurements.csv"
                )
                rejected += 1
                continue

            # 🛠️ 3. CLEAN PATHWAY BRANCH: Typecast metrics values and flush downstream
            result = connection.execute(
                text(sql),
                {
                    "source_record_id": source_record_id,
                    "equipment_id": int(record["equipment_id"]),
                    "site_id": int(record["site_id"]),
                    "measured_at": temp_record["measured_at"],
                    "traffic_mb": float(record["traffic_mb"]),
                    "latency_ms": float(record["latency_ms"]),
                    "packet_loss_pct": float(record["packet_loss_pct"]),
                    "signal_strength_dbm": float(record["signal_strength_dbm"]),
                    "availability_pct": float(record["availability_pct"])
                }
            )
            inserted += result.rowcount
            
            # Update the processed set to handle in-batch duplicates dynamically
            if result.rowcount == 1:
                processed_ids.add(source_record_id)

    return inserted, rejected, skipped


def run_ingestion():
    """Unified ingestion runner module entry point."""
    logger.info("--- INGESTION LAYER ---")

    records = read_measurements()
    source_records = len(records)
    
    inserted, rejected, skipped = insert_measurements(records)

    logger.info(
        "Incremental ingestion completed | "
        f"source_records={source_records} | "
        f"inserted={inserted} | "
        f"rejected={rejected} | "
        f"skipped={skipped}"
    )

    return {
        "source_records": source_records,
        "inserted_records": inserted,
        "rejected_records": rejected,
        "skipped_records": skipped
    }


if __name__ == "__main__":
    run_ingestion()
