import logging
import time
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import text

# Load environment configuration variables immediately upon package boot
load_dotenv()

from src.config import DATABASE_URL, PIPELINE_NAME
from src.database import engine
from src.logging_config import configure_logging
from src.pipeline_tracking import start_stage, finish_stage  # 🔑 Newly Imported!
from src.transformation.silver import run_silver
from src.data_quality.quality_gate import run_quality_gate
from src.transformation.gold import run_gold

# Instantiate module-level logging context handle wrapper
logger = logging.getLogger(__name__)


def start_pipeline_run():
    """Initializes a new tracking run record inside the database registry."""
    sql = """
    INSERT INTO pipeline_runs (
        pipeline_name, started_at, status, current_stage, records_processed, duration_seconds
    )
    VALUES (
        :pipeline_name, CURRENT_TIMESTAMP, 'RUNNING', 'STARTING', 0, 0.000
    )
    RETURNING run_id;
    """
    with engine.begin() as connection:
        return connection.execute(
            text(sql),
            {
                "pipeline_name": PIPELINE_NAME,
            }
        ).scalar()


def update_pipeline_stage(run_id, stage):
    """Dynamically updates the active pipeline processing phase on disk."""
    sql = """
    UPDATE pipeline_runs
    SET current_stage = :current_stage
    WHERE run_id = :run_id;
    """
    with engine.begin() as connection:
        connection.execute(
            text(sql),
            {
                "run_id": run_id,
                "current_stage": stage,
            }
        )


def finish_pipeline_run(
    run_id,
    status,
    records_processed=0,
    error_message=None,
    duration_seconds=None,
    current_stage=None
):
    """Closes out the pipeline execution run tracking state with final parameters."""
    sql = """
    UPDATE pipeline_runs
    SET completed_at = :completed_at,
        status = :status,
        records_processed = :records_processed,
        error_message = :error_message,
        duration_seconds = :duration_seconds,
        current_stage = COALESCE(:current_stage, current_stage)
    WHERE run_id = :run_id;
    """
    with engine.begin() as connection:
        connection.execute(
            text(sql),
            {
                "run_id": run_id,
                "completed_at": datetime.now(),
                "status": status,
                "records_processed": records_processed,
                "error_message": error_message,
                "duration_seconds": duration_seconds,
                "current_stage": current_stage,
            }
        )


def main():
    """Unified data pipeline stage engine equipped with high-resolution logging timers."""
    # 🚀 Boot up centralized logger configurations before any execution logic runs
    configure_logging()
    
    logger.info("=" * 60)
    logger.info("STARTING UGANDA NETWORK & SERVICE INTELLIGENCE PIPELINE RUN")
    logger.info("=" * 60)

    # Begin global clock timer tracking pass
    pipeline_start = time.perf_counter()
    
    run_id = start_pipeline_run()
    logger.info(f"Pipeline tracking run record successfully created. run_id={run_id}")

    global_records_processed = 0
    try:
        # -------------------------------------------------
        # 2. SILVER STAGE
        # -------------------------------------------------
        update_pipeline_stage(run_id, "SILVER")
        silver_sid = start_stage(run_id, "SILVER")  # 🚀 Start Stage
        
        try:
            silver_start = time.perf_counter()
            logger.info("Starting SILVER stage")
            global_records_processed = run_silver(run_id)
            silver_duration = time.perf_counter() - silver_start
            
            finish_stage(silver_sid, "SUCCESS", records_processed=global_records_processed)  # 💾 Finish Stage
            logger.info(f"SILVER stage completed in {silver_duration:.2f} seconds | records_processed={global_records_processed}")
        except Exception as exc:
            finish_stage(silver_sid, "FAILED", error_message=str(exc))
            logger.exception("SILVER stage failed ❌")
            raise

        # -------------------------------------------------
        # 3. QUALITY STAGE
        # -------------------------------------------------
        update_pipeline_stage(run_id, "QUALITY")
        quality_sid = start_stage(run_id, "QUALITY")  # 🚀 Start Stage
        
        try:
            quality_start = time.perf_counter()
            logger.info("Starting QUALITY stage")
            quality_result = run_quality_gate(run_id)
            quality_duration = time.perf_counter() - quality_start

            finish_stage(quality_sid, "SUCCESS")  # 💾 Finish Stage
            if quality_result["failed"] > 0:
                logger.warning(f"⚠️ Quality anomalies detected for run_id={run_id} | Failed counts={quality_result['failed']}")
                logger.info(f"QUALITY stage completed with warnings in {quality_duration:.2f} seconds")
            else:
                logger.info(f"QUALITY stage completed in {quality_duration:.2f} seconds with 0 rule breaches.")
        except Exception as exc:
            finish_stage(quality_sid, "FAILED", error_message=str(exc))
            logger.exception("QUALITY stage failed ❌")
            raise

        # -------------------------------------------------
        # 4. GOLD STAGE
        # -------------------------------------------------
        update_pipeline_stage(run_id, "GOLD")
        gold_sid = start_stage(run_id, "GOLD")  # 🚀 Start Stage
        
        try:
            gold_start = time.perf_counter()
            logger.info("Starting GOLD stage")
            run_gold(run_id)
            gold_duration = time.perf_counter() - gold_start
            
            finish_stage(gold_sid, "SUCCESS")  # 💾 Finish Stage
            logger.info(f"GOLD stage completed in {gold_duration:.2f} seconds.")
        except Exception as exc:
            finish_stage(gold_sid, "FAILED", error_message=str(exc))
            logger.exception("GOLD stage failed ❌")
            raise

        # Compute complete transaction duration metrics from perf counter
        total_duration = time.perf_counter() - pipeline_start

        # -------------------------------------------------
        # 5. SUCCESS PATH CLOSEOUT
        # -------------------------------------------------
        finish_pipeline_run(
            run_id=run_id,
            status="SUCCESS",
            records_processed=global_records_processed,
            duration_seconds=total_duration,
            current_stage="SUCCESS"
        )
        logger.info("============================================================")
        logger.info(f"Pipeline completed successfully in {total_duration:.2f} seconds 🎉")
        logger.info(f"Total delta records processed: {global_records_processed}")
        logger.info("============================================================")

    except Exception as error:
        total_duration = time.perf_counter() - pipeline_start

        # -------------------------------------------------
        # 6. FAILURE PATH CLOSEOUT
        # -------------------------------------------------
        finish_pipeline_run(
            run_id=run_id,
            status="FAILED",
            records_processed=0,
            error_message=str(error),
            duration_seconds=total_duration,
            current_stage=None
        )
        logger.exception(f"Pipeline failed after {total_duration:.2f} seconds ❌")
        raise


if __name__ == "__main__":
    main()
