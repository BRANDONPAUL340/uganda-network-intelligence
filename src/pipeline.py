from datetime import datetime
import time

from sqlalchemy import text

from src.database import engine
from src.ingestion.measurements import run_ingestion
from src.logger import get_logger
from src.quality import run_quality_checks
from src.transformation.silver import run_silver
from src.transformation.gold import run_incremental_gold


# Initialize our central orchestrator logger utility instance
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
    logger.info("UGANDA NETWORK & SERVICE INTELLIGENCE ORCHESTRATOR")
    logger.info("=" * 60)

    start_time = time.perf_counter()

    run_id = start_pipeline_run()

    logger.info(f"Pipeline run ID: {run_id}")

    records_read = 0
    records_processed = 0
    records_rejected = 0

    try:
        # -------------------------------------------------
        # 1. INGESTION
        # -------------------------------------------------
        logger.info("--- INGESTION ---")
        ingestion_result = run_ingestion()

        records_read = ingestion_result["records_read"]
        records_processed = ingestion_result["records_inserted"]
        records_rejected = ingestion_result["records_rejected"]

        logger.info(f"Records read: {records_read}")
        logger.info(f"Records inserted: {records_processed}")
        logger.info(f"Records rejected: {records_rejected}")
        logger.info(f"Duplicates: {ingestion_result['duplicates']}")

        # -------------------------------------------------
        # 2. DATA QUALITY
        # -------------------------------------------------
        logger.info("--- DATA QUALITY ---")
        run_quality_checks()

        # -------------------------------------------------
        # 3. SILVER
        # -------------------------------------------------
        logger.info("--- SILVER ---")
        silver_result = run_silver()

        logger.info(f"Silver measurements loaded: {silver_result['measurements_loaded']}")
        logger.info(f"Silver health records loaded: {silver_result['health_loaded']}")

        # -------------------------------------------------
        # 4. GOLD
        # -------------------------------------------------
        logger.info("--- GOLD ---")
        run_incremental_gold()

        # -------------------------------------------------
        # 5. SUCCESS
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

        logger.info("Pipeline completed successfully.")
        logger.info(f"Execution time: {duration:.3f} seconds")

    except Exception as error:
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

        logger.error("Pipeline failed.")
        logger.error(f"Error: {error}")
        raise


if __name__ == "__main__":
    main()
