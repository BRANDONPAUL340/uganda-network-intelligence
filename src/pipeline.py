from datetime import datetime
import time

from sqlalchemy import text

from src.database import engine
from src.ingestion.measurements import run_ingestion
from src.logger import get_logger
from src.quality import run_quality_checks
from src.transformation.silver import run_silver
from src.transformation.gold import run_gold


# Initialize our central orchestrator logger utility
logger = get_logger(__name__)

PIPELINE_NAME = "uganda_network_intelligence"


def start_pipeline_run():
    """
    Create a new pipeline audit record.
    """
    sql = """
    INSERT INTO pipeline_runs (
        pipeline_name,
        started_at,
        status
    )
    VALUES (
        :pipeline_name,
        :started_at,
        'RUNNING'
    )
    RETURNING run_id;
    """
    with engine.begin() as connection:
        result = connection.execute(
            text(sql),
            {
                "pipeline_name": PIPELINE_NAME,
                "started_at": datetime.now(),
            }
        )
        return result.scalar()


def finish_pipeline_run(
    run_id,
    status,
    records_read=0,
    records_processed=0,
    records_rejected=0,
    duration_seconds=0,
    error_message=None
):
    """
    Update the pipeline audit record when the run finishes.
    """
    sql = """
    UPDATE pipeline_runs
    SET
        completed_at = :completed_at,
        status = :status,
        records_read = :records_read,
        records_processed = :records_processed,
        records_rejected = :records_rejected,
        duration_seconds = :duration_seconds,
        error_message = :error_message
    WHERE run_id = :run_id;
    """
    with engine.begin() as connection:
        connection.execute(
            text(sql),
            {
                "run_id": run_id,
                "completed_at": datetime.now(),
                "status": status,
                "records_read": records_read,
                "records_processed": records_processed,
                "records_rejected": records_rejected,
                "duration_seconds": duration_seconds,
                "error_message": error_message,
            }
        )


def main():
    logger.info("=" * 60)
    logger.info("UGANDA NETWORK & SERVICE INTELLIGENCE CONDUCTOR")
    logger.info("=" * 60)

    # Start performance runtime clock
    start_time = time.perf_counter()

    # Open our system audit run log entry ticket
    run_id = start_pipeline_run()
    logger.info(f"Pipeline run ID initiated: {run_id}")

    # Set up our volumetric balancing counter fields baseline
    records_read = 0
    records_processed = 0
    records_rejected = 0

    try:
        # -------------------------------------------------
        # 1. BRONZE FILE INGESTION LAYER
        # -------------------------------------------------
        logger.info("Triggering Stage 1: Bronze File Ingestion Layer...")
        ingest_result = run_ingestion()
        
        # Pull dynamic file loading stats to populate audit log metrics
        records_read = ingest_result.get("records_read", 0)
        records_rejected = ingest_result.get("records_rejected", 0)

        # -------------------------------------------------
        # 2. DATA QUALITY GATEWAY FIREWALL
        # -------------------------------------------------
        logger.info("Triggering Stage 2: Data Quality Gateway validation checks...")
        run_quality_checks()

        # -------------------------------------------------
        # 3. SILVER INCREMENTAL TRANSFORMATION
        # -------------------------------------------------
        logger.info("Triggering Stage 3: Silver Layer processing tier...")
        silver_result = run_silver()
        
        if isinstance(silver_result, dict):
            records_processed = silver_result.get("measurements_loaded", 0)
        else:
            records_processed = silver_result if silver_result is not None else 0

        # -------------------------------------------------
        # 4. GOLD ANALYTICAL SUMMARIZATION
        # -------------------------------------------------
        logger.info("Triggering Stage 4: Gold Layer analytical summarization...")
        run_gold()

        # -------------------------------------------------
        # 5. SUCCESS EXECUTION CLOSEOUT
        # -------------------------------------------------
        duration = time.perf_counter() - start_time

        finish_pipeline_run(
            run_id=run_id,
            status="SUCCESS",
            records_read=records_read,
            records_processed=records_processed,
            records_rejected=records_rejected,
            duration_seconds=duration
        )
        logger.info("🎉 COMPLETE PIPELINE ORCHESTRATION FINISHED WITH SUCCESS")
        logger.info(f"Total execution time: {duration:.3f} seconds")

    except Exception as error:
        # -------------------------------------------------
        # 6. EXCEPTION CRASH HANDLING TRACKING
        # -------------------------------------------------
        duration = time.perf_counter() - start_time

        finish_pipeline_run(
            run_id=run_id,
            status="FAILED",
            records_read=records_read,
            records_processed=records_processed,
            records_rejected=records_rejected,
            duration_seconds=duration,
            error_message=str(error)
        )
        logger.error("❌ PIPELINE RUN ENCOUNTERED AN EXCEPTION FAILURE CRASH")
        logger.error(f"Execution turnaround time prior to abort: {duration:.3f} seconds")
        logger.exception("Captured Exception Trace details:")
        raise


if __name__ == "__main__":
    main()
