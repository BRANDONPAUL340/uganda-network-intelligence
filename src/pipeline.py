from datetime import datetime
import time

from sqlalchemy import text

from src.database import engine
from src.logger import get_logger
from src.quality import run_quality_checks
from src.transformation.silver import run_silver
from src.transformation.gold import run_gold


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
    records_inserted=0,
    records_rejected=0,
    silver_records_processed=0,
    gold_records_processed=0,
    error_message=None
):
    """
    Update the pipeline audit record with end-to-end metrics when the run finishes.
    """
    sql = """
    UPDATE pipeline_runs
    SET
        completed_at = :completed_at,
        duration_seconds = EXTRACT(EPOCH FROM (:completed_at - started_at)),
        status = :status,
        records_read = :records_read,
        records_inserted = :records_inserted,
        records_rejected = :records_rejected,
        silver_records_processed = :silver_records_processed,
        gold_records_processed = :gold_records_processed,
        records_processed = :records_inserted,
        error_message = :error_message
    WHERE run_id = :run_id;
    """

    completed_at = datetime.now()

    with engine.begin() as connection:
        connection.execute(
            text(sql),
            {
                "run_id": run_id,
                "completed_at": completed_at,
                "status": status,
                "records_read": records_read,
                "records_inserted": records_inserted,
                "records_rejected": records_rejected,
                "silver_records_processed": silver_records_processed,
                "gold_records_processed": gold_records_processed,
                "error_message": error_message,
            }
        )


def main():
    logger.info("=" * 60)
    logger.info("UGANDA NETWORK & SERVICE INTELLIGENCE ORCHESTRATOR")
    logger.info("=" * 60)

    run_id = start_pipeline_run()
    logger.info(f"Pipeline run ID: {run_id}")

    # Initialize metrics dictionaries cleanly
    ingestion_metrics = {}
    silver_metrics = {}
    gold_metrics = {}

    try:
        # -------------------------------------------------
        # 1. INGESTION
        # -------------------------------------------------
        logger.info("--- INGESTION ---")
        from src.ingestion.measurements import run_ingestion
        ingestion_metrics = run_ingestion()

        # -------------------------------------------------
        # 2. DATA QUALITY
        # -------------------------------------------------
        logger.info("--- DATA QUALITY ---")
        run_quality_checks()

        # -------------------------------------------------
        # 3. SILVER
        # -------------------------------------------------
        logger.info("--- SILVER ---")
        silver_metrics = run_silver()

        # -------------------------------------------------
        # 4. GOLD
        # -------------------------------------------------
        logger.info("--- GOLD ---")
        gold_metrics = run_gold()

        # -------------------------------------------------
        # 5. SUCCESS
        # -------------------------------------------------
        finish_pipeline_run(
            run_id=run_id,
            status="SUCCESS",
            records_read=ingestion_metrics.get("records_read", 0),
            records_inserted=ingestion_metrics.get("records_inserted", 0),
            records_rejected=ingestion_metrics.get("records_rejected", 0),
            silver_records_processed=silver_metrics.get("measurements_loaded", 0),
            gold_records_processed=gold_metrics.get("gold_records_processed", 0)
        )
        logger.info("Pipeline completed successfully.")

    except Exception as error:
        # -------------------------------------------------
        # 6. FAILURE
        # -------------------------------------------------
        finish_pipeline_run(
            run_id=run_id,
            status="FAILED",
            records_read=ingestion_metrics.get("records_read", 0),
            records_inserted=ingestion_metrics.get("records_inserted", 0),
            records_rejected=ingestion_metrics.get("records_rejected", 0),
            silver_records_processed=silver_metrics.get("measurements_loaded", 0),
            gold_records_processed=gold_metrics.get("gold_records_processed", 0),
            error_message=str(error)
        )
        logger.error("Pipeline failed.")
        logger.error(f"Error: {error}")
        raise


if __name__ == "__main__":
    main()
