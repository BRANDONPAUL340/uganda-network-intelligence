import logging
from pathlib import Path
from src.ingestion.csv_loader import read_measurements_csv
from src.ingestion.api_loader import normalize_api_record
from src.ingestion.raw_loader import load_raw_records
from src.ingestion.batch_tracking import start_ingestion_batch, finish_ingestion_batch

logger = logging.getLogger(__name__)


def ingest_csv(file_path, ingestion_run_id):
    """
    Orchestrates the extraction and parsing loop for external CSV dumps.
    Registers an audit batch tracking lifecycle entry and binds it to raw rows.
    """
    file_path = Path(file_path)
    logger.info(f"Initializing logged CSV ingestion sweep for file: [{file_path.name}]")
    
    # 🕵️─┐ Step 1: Initialize the tracking batch record row
    batch_id = start_ingestion_batch(
        pipeline_run_id=ingestion_run_id,
        source_type="CSV",
        source_name=file_path.name
    )

    try:
        raw_records = read_measurements_csv(file_path)
        records_received = len(raw_records)
        normalized_records = []

        for record in raw_records:
            normalized_records.append({
                "measurement_id": int(record["measurement_id"]),
                "site_id": int(record["site_id"]),
                "equipment_id": int(record["equipment_id"]),
                "measurement_date": record["measurement_date"],
                "traffic_mb": float(record["traffic_mb"]),
                "latency_ms": float(record["latency_ms"]),
                "packet_loss_pct": float(record["packet_loss_pct"]),
                "signal_strength_dbm": float(record["signal_strength_dbm"]),
                "availability_pct": float(record["availability_pct"]),
            })

        # Step 2: Batch commit records straight into the raw tier with batch lineage context
        records_loaded = load_raw_records(
            normalized_records,
            ingestion_run_id=ingestion_run_id,
            source_file=file_path.name,
            ingestion_batch_id=batch_id,
        )

        # 🕵️─┐ Step 3: Close out the tracking block with a clean SUCCESS state
        finish_ingestion_batch(
            batch_id=batch_id,
            status="SUCCESS",
            records_received=records_received,
            records_loaded=records_loaded
        )
        return records_loaded

    except Exception as e:
        error_msg = f"Fatal CSV Ingestion collapse: {str(e)}"
        logger.error(error_msg)
        finish_ingestion_batch(
            batch_id=batch_id,
            status="FAILED",
            records_received=0,
            records_loaded=0,
            error_message=error_msg
        )
        raise


def ingest_api(records, ingestion_run_id):
    """
    Orchestrates ingestion validation loops for live API JSON arrays.
    Registers an audit batch tracking lifecycle entry and binds it to raw rows.
    """
    logger.info(f"Initializing logged stream API JSON ingestion runner pass for {len(records)} records...")
    
    # 🕵️─┐ Step 1: Initialize the tracking batch record row
    batch_id = start_ingestion_batch(
        pipeline_run_id=ingestion_run_id,
        source_type="API",
        source_name="api_measurements"
    )

    try:
        records_received = len(records)
        normalized_records = [
            normalize_api_record(record)
            for record in records
        ]

        # Step 2: Batch commit records straight into the raw tier with batch lineage context
        records_loaded = load_raw_records(
            normalized_records,
            ingestion_run_id=ingestion_run_id,
            source_file="api_measurements",
            ingestion_batch_id=batch_id,
        )

        # 🕵️─┐ Step 3: Close out the tracking block with a clean SUCCESS state
        finish_ingestion_batch(
            batch_id=batch_id,
            status="SUCCESS",
            records_received=records_received,
            records_loaded=records_loaded
        )
        return records_loaded

    except Exception as e:
        error_msg = f"Fatal API Ingestion collapse: {str(e)}"
        logger.error(error_msg)
        finish_ingestion_batch(
            batch_id=batch_id,
            status="FAILED",
            records_received=0,
            records_loaded=0,
            error_message=error_msg
        )
        raise
