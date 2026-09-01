from datetime import datetime
import time

from sqlalchemy import text

from src.database import engine
from src.ingestion.measurements import run_ingestion
from src.logger import get_logger
from src.data_quality.checks import run_data_quality_checks  # 🔑 Updated Package Import Link
from src.transformation.silver import run_silver
from src.transformation.gold import run_gold


PIPELINE_NAME = "uganda_network_intelligence"

# Initialize central master pipeline orchestrator logger
logger = get_logger(__name__)


def start_pipeline_run():
    logger.info("Creating pipeline run record in the database.")
    sql = """
    INSERT INTO pipeline_runs (pipeline_name, started_at, status)
    VALUES (:pipeline_name, :started_at, 'RUNNING')
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
        run_id = result.scalar()
        logger.info("Pipeline run record created. run_id=%s", run_id)
        return run_id


def finish_pipeline_run(
    run_id, status, records_read=0, records_inserted=0, records_rejected=0,
    silver_records_processed=0, gold_records_processed=0,
    quality_checks_run=0, quality_checks_failed=0, error_message=None
):
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
        quality_checks_run = :quality_checks_run,
        quality_checks_failed = :quality_checks_failed,
        records_processed = :records_inserted,
        error_message = :error_message
    WHERE run_id = :run_id;
    """
    completed_at = datetime.now()
    with engine.begin() as connection:
        connection.execute(
            text(sql),
            {
                "run_id": run_id, "completed_at": completed_at, "status": status,
                "records_read": records_read, "records_inserted": records_inserted, "records_rejected": records_rejected,
                "silver_records_processed": silver_records_processed, "gold_records_processed": gold_records_processed,
                "quality_checks_run": quality_checks_run, "quality_checks_failed": quality_checks_failed,
                "error_message": error_message,
            }
        )
    logger.info("Pipeline run closed. run_id=%s status=%s records_read=%s", run_id, status, records_read)


def main():
    logger.info("=" * 60)
    logger.info("UGANDA NETWORK & SERVICE INTELLIGENCE ORCHESTRATOR")
    logger.info("=" * 60)

    # Initialize tracking states
    ingestion_metrics = {}
    silver_metrics = {}
    gold_metrics = {}
    quality_passed = False

    run_id = start_pipeline_run()
    logger.info("Pipeline run started. run_id=%s", run_id)

    try:
        # 1. INGESTION
        logger.info("Starting ingestion stage.")
        ingestion_metrics = run_ingestion()
        logger.info("Ingestion stage completed.")

        # 2. DATA QUALITY SECURITY GATEWAY FIREWALL
        logger.info("Starting data quality stage.")
        quality_passed = run_data_quality_checks()

        if not quality_passed:
            raise RuntimeError("Data-quality checks failed. Pipeline stopped before Silver.")
        logger.info("Data quality gate passed.")

        # 3. SILVER TRANSFORMS
        logger.info("Starting Silver transformation.")
        silver_metrics = run_silver()
        logger.info("Silver transformation completed.")

        # 4. GOLD AGGREGATIONS
        logger.info("Starting Gold transformation.")
        gold_metrics = run_gold()
        logger.info("Gold transformation completed.")

        # 5. SUCCESS COMMITS
        finish_pipeline_run(
            run_id=run_id, status="SUCCESS",
            records_read=ingestion_metrics.get("records_read", 0),
            records_inserted=ingestion_metrics.get("records_inserted", 0),
            records_rejected=ingestion_metrics.get("records_rejected", 0),
            silver_records_processed=silver_metrics.get("measurements_loaded", 0),
            gold_records_processed=gold_metrics.get("gold_records_processed", 0),
            quality_checks_run=3, quality_checks_failed=0
        )
        logger.info("🎉 Complete Medallion architecture chain finished successfully.")

    except Exception as error:
        # 6. FAILURE ERROR LOGGING TRAPS
        logger.exception("Pipeline failed. run_id=%s", run_id)
        finish_pipeline_run(
            run_id=run_id, status="FAILED",
            records_read=ingestion_metrics.get("records_read", 0),
            records_inserted=ingestion_metrics.get("records_inserted", 0),
            records_rejected=ingestion_metrics.get("records_rejected", 0),
            silver_records_processed=silver_metrics.get("measurements_loaded", 0),
            gold_records_processed=gold_metrics.get("gold_records_processed", 0),
            quality_checks_run=3, quality_checks_failed=0 if quality_passed else 1,
            error_message=str(error)
        )
        raise


if __name__ == "__main__":
    main()
