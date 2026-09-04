from datetime import datetime
import time

from sqlalchemy import text

from src.config import PIPELINE_NAME
from src.database import engine
from src.ingestion.measurements import run_ingestion
from src.logger import get_logger
from src.monitoring import PipelineMetrics  # 🔑 Object-Oriented Telemetry
from src.data_quality.checks import run_data_quality_checks
from src.transformation.silver import run_silver
from src.transformation.gold import run_gold

# Initialize central master pipeline orchestrator logger instance
logger = get_logger(__name__)


def start_pipeline_run(source_file=None):
    """Initializes a new continuous integration runtime tracking session entry."""
    logger.info("Creating pipeline run record in the database.")
    sql = """
    INSERT INTO pipeline_runs (
        pipeline_name, source_file, started_at, status,
        records_read, records_inserted, records_rejected, records_skipped, records_processed
    )
    VALUES (
        :pipeline_name, :source_file, :started_at, 'RUNNING',
        0, 0, 0, 0, 0
    )
    RETURNING run_id;
    """
    with engine.begin() as connection:
        result = connection.execute(
            text(sql),
            {
                "pipeline_name": PIPELINE_NAME,
                "source_file": source_file,
                "started_at": datetime.now(),
            }
        )
        run_id = result.scalar()
        logger.info(f"Pipeline run record created in database. run_id={run_id}")
        return run_id


def finish_pipeline_run(
    run_id,
    status,
    records_read=0,
    records_inserted=0,
    records_rejected=0,
    records_skipped=0,
    quality_checks_passed=0,
    silver_records_processed=0,
    gold_records_processed=0,
    error_message=None,
):
    """Closes out the active pipeline execution log with high-precision duration metadata."""
    sql = """
    UPDATE pipeline_runs
    SET
        completed_at = :completed_at,
        status = :status,
        records_read = :records_read,
        records_inserted = :records_inserted,
        records_rejected = :records_rejected,
        records_skipped = :records_skipped,
        records_processed = (:records_inserted + :records_rejected),
        duration_seconds = EXTRACT(EPOCH FROM (:completed_at - started_at)),
        quality_checks_passed = :quality_checks_passed,
        silver_records_processed = :silver_records_processed,
        gold_records_processed = :gold_records_processed,
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
                "records_skipped": records_skipped,
                "quality_checks_passed": quality_checks_passed,
                "silver_records_processed": silver_records_processed,
                "gold_records_processed": gold_records_processed,
                "error_message": error_message,
            }
        )


def main():
    pipeline_start = time.time()

    print("=" * 60)
    print("UGANDA NETWORK & SERVICE INTELLIGENCE")
    print("=" * 60)

    # 🚀 Instantiate our unified object-oriented metrics manager
    metrics = PipelineMetrics()

    # Initialize tracking metric holders to guarantee safety boundary defaults
    silver_metrics = {"measurements_loaded": 0, "health_loaded": 0}
    gold_metrics = {"site_daily_performance": 0, "equipment_health": 0}
    quality_checks_passed = 0
    quality_passed = False

    target_file = "network_measurements.csv"
    run_id = start_pipeline_run(source_file=target_file)
    print(f"\nPipeline run ID: {run_id}")
    logger.info(f"Pipeline run started | run_id={run_id}")

    try:
        # -------------------------------------------------
        # 1. INGESTION WITH INTEGRATED DATA QUARANTINE & CDC
        # -------------------------------------------------
        logger.info(f"Starting ingestion stage | run_id={run_id}")
        ingestion_result = run_ingestion()
        
        # 📊 Route returns cleanly straight into our object model attributes
        metrics.records_read = ingestion_result["source_records"]
        metrics.records_inserted = ingestion_result["inserted_records"]
        metrics.records_rejected = ingestion_result["rejected_records"]
        metrics.records_skipped = ingestion_result["skipped_records"]
        
        print("\nIngestion summary:")
        print(f"  Source records:   {metrics.records_read}")
        print(f"  Inserted records: {metrics.records_inserted}")
        print(f"  Rejected records: {metrics.records_rejected}")
        print(f"  Skipped records:  {metrics.records_skipped}")
        logger.info(f"Ingestion stage completed successfully | run_id={run_id}")

        # -------------------------------------------------
        # 2. DATA QUALITY VALIDATION GATEWAY
        # -------------------------------------------------
        logger.info("Starting data-quality checks")
        quality_response = run_data_quality_checks()
        
        quality_passed = quality_response["passed"]
        quality_checks_passed = sum(
            1 for passed in quality_response["checks"].values() if passed
        )

        if not quality_passed:
            logger.error(f"Data-quality checks failed | run_id={run_id}")
            finish_pipeline_run(
                run_id=run_id,
                status="FAILED",
                records_read=metrics.records_read,
                records_inserted=metrics.records_inserted,
                records_rejected=metrics.records_rejected,
                records_skipped=metrics.records_skipped,
                quality_checks_passed=quality_checks_passed,
                error_message="Data-quality checks failed"
            )
            raise RuntimeError("Data-quality checks failed. Pipeline stopped before Silver.")

        logger.info(f"Data-quality checks passed | run_id={run_id}")

        # -------------------------------------------------
        # 3. SILVER TRANSFORMS
        # -------------------------------------------------
        logger.info(f"Starting Silver transformation | run_id={run_id}")
        silver_metrics = run_silver(run_id)
        print(f"Silver measurements loaded: {silver_metrics['measurements_loaded']}")
        logger.info(f"Silver transformation completed | run_id={run_id}")

        # -------------------------------------------------
        # 4. GOLD REPORTING AGGREGATIONS
        # -------------------------------------------------
        logger.info(f"Starting Gold transformation | run_id={run_id}")
        gold_metrics = run_gold(run_id)
        
        gold_records = (
            gold_metrics["site_daily_performance"]
            + gold_metrics["equipment_health"]
        )
        logger.info(f"Gold transformation completed | run_id={run_id}")

        # Compute precision runtime delta metrics
        pipeline_duration = time.time() - pipeline_start

            # -------------------------------------------------
        # 5. SUCCESS PATH CLOSEOUT
        # -------------------------------------------------
        finish_pipeline_run(
            run_id=run_id,
            status="SUCCESS",
            records_read=metrics.records_read,
            records_inserted=metrics.records_inserted,
            records_rejected=metrics.records_rejected,
            records_skipped=metrics.records_skipped,
            quality_checks_passed=quality_checks_passed,
            silver_records_processed=silver_metrics["measurements_loaded"],
            gold_records_processed=gold_records
        )

        
        logger.info(
            f"Pipeline completed successfully | run_id={run_id} | "
            f"source_records={metrics.records_read} | duration_seconds={pipeline_duration:.2f}"
        )
        
        print("\nPipeline summary")
        print("-" * 40)
        print(f"Records read:       {metrics.records_read}")
        print(f"Records inserted:   {metrics.records_inserted}")
        print(f"Records rejected:   {metrics.records_rejected}")
        print(f"Records skipped:    {metrics.records_skipped}")
        print(f"Records processed:  {metrics.records_processed}")
        print("\nPipeline completed successfully.")

    except Exception as error:
        # -------------------------------------------------
        # 6. FAILURE PATH OVERRIDES
        # -------------------------------------------------
        logger.error(f"Pipeline failed | run_id={run_id} | error={error}")

        finish_pipeline_run(
            run_id=run_id,
            status="FAILED",
            records_read=metrics.records_read,
            records_inserted=metrics.records_inserted,
            records_rejected=metrics.records_rejected,
            records_skipped=metrics.records_skipped,
            quality_checks_passed=quality_checks_passed,
            silver_records_processed=silver_metrics.get("measurements_loaded", 0),
            gold_records_processed=0,
            error_message=str(error)
        )
        print("\nPipeline failed.")
        print(f"Error: {error}")
        raise


if __name__ == "__main__":
    main()
